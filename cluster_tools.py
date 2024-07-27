import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer

import config
from read_files import load_arrays

def cluster_image():
    # NOTE: Label data (y) is read and processed throughout to ensure shapes and masks are consistent
    # but this label data is not used in the clustering process; only for evaluation later
    
    # Check there is only one image marked for clustering (current setup, could be changed)
    true_count = sum(1 for paths in config.enmap_data.values() if paths.get('cluster', False))
    if true_count == 1:
        area_code = None
        for paths in config.enmap_data.values():
            if paths.get("cluster", False):
                area_code = paths.get("area_code")
                break
        X, y = load_arrays(area_code) # Load the image and reference data
    else:
        raise ValueError("Only one image should be marked for clustering in the current setup")

    # Flatten the images for spectral only clustering
    num_rows, num_cols, num_bands = X.shape
    X_reshaped = X.reshape((num_rows * num_cols, num_bands))
    y_reshaped = y.flatten()

    # Create a mask for valid pixels
    valid_mask = (~np.isnan(X_reshaped).any(axis=1)) & (y_reshaped != -1) & (y_reshaped != 0)

    # Filter valid pixels
    X_valid = X_reshaped[valid_mask]
    y_valid = y_reshaped[valid_mask]

    # Impute NaN values with the mean of each band (could be more complex, but NaNs are rare)
    imputer = SimpleImputer(strategy='mean')
    X_imputed = imputer.fit_transform(X_valid)

    # Apply K-Means clustering
    n_clusters = 10  # Clusters equal to ESA worldcover for now
    print(f"Applying K-Means clustering with {n_clusters} clusters")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans_labels = kmeans.fit_predict(X_imputed)

    # Reshape the clustered result back to 2D
    clustered_image = np.full((num_rows * num_cols), -1)  # -1 for masked areas
    clustered_image[valid_mask] = kmeans_labels
    clustered_image = clustered_image.reshape((num_rows, num_cols))

    # Mask the -1 values
    masked_clustered_image = np.ma.masked_where(clustered_image == -1, clustered_image)

    # Map y_valid values to a contiguous range starting from 0
    unique_classes = np.unique(y_valid)
    class_map = {value: idx for idx, value in enumerate(unique_classes)}
    y_mapped = np.vectorize(class_map.get)(y_valid)

    n_classes = len(unique_classes)
    overlap_matrix = np.zeros((n_classes, n_clusters))
    accuracy_matrix = np.zeros((n_classes, n_clusters))

    # Record the cross-over against ESA classification data
    for i in range(n_classes):
        for j in range(n_clusters):
            overlap_matrix[i, j] = np.sum((y_mapped == i) & (kmeans_labels == j))
            accuracy_matrix[i, j] = np.sum((y_mapped == i) & (kmeans_labels == j)) / np.sum(y_mapped == i)

    # Create a comparison plot
    fig, axs = plt.subplots(2, 2, figsize=(10, 10))

    # Plot ESA label data (y)
    cmap = plt.get_cmap('tab10')
    cmap.set_bad(color='white') # Blank out masked areas
    im1 = axs[0, 0].imshow(y.reshape(num_rows, num_cols), cmap=cmap)
    axs[0, 0].set_title('ESA Labelled data')
    cbar1 = fig.colorbar(im1, ax=axs[0, 0], fraction=0.046, pad=0.04)
    cbar1.set_ticks(unique_classes)
    cbar1.set_ticklabels(range(len(unique_classes)))
    axs[0, 0].set_xlabel('Column Index')
    axs[0, 0].set_ylabel('Row Index')

    # Plot the clustered image
    cmap = plt.get_cmap('tab10')
    cmap.set_bad(color='white')  # Blank out masked areas
    im2 = axs[0, 1].imshow(masked_clustered_image, cmap=cmap)
    axs[0, 1].set_title('K-Means Clustering')
    fig.colorbar(im2, ax=axs[0, 1], fraction=0.046, pad=0.04)
    axs[0, 1].set_xlabel('Column Index')
    axs[0, 1].set_ylabel('Row Index')

    # Plot the overlap matrix to show the cross-over between ESA and clustering
    sns.heatmap(overlap_matrix, annot=True, fmt='.0f', cmap='viridis', ax=axs[1, 0])
    axs[1, 0].set_title('Overlap Matrix')
    axs[1, 0].set_xlabel('Cluster ID')
    axs[1, 0].set_ylabel('ESA Classification')

    # Plot the accuracy matrix to show the normalised cross-over of the clustering
    sns.heatmap(accuracy_matrix, annot=True, fmt='.2f', cmap='viridis', ax=axs[1, 1])
    axs[1, 1].set_title('Accuracy Matrix')
    axs[1, 1].set_xlabel('Cluster ID')
    axs[1, 1].set_ylabel('ESA Classification')

    plt.tight_layout()
    plt.show()
