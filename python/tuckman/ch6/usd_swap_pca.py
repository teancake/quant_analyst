import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
def get_data():
    base_dir = "./usd_swap"
    df = None
    for i in [1, 2, 3, 4, 5, 7, 10, 30]:
        fn = os.path.join(base_dir, f"DSWP{i}.csv")
        print(fn)
        temp_df = pd.read_csv(fn, index_col="DATE", parse_dates=["DATE"], )
        if df is None:
            df = temp_df
        else:
            df = pd.merge(df, temp_df, left_index=True, right_index=True)
    df = df.replace(to_replace=".", value=pd.NA)
    df = df.dropna()
    df = df.astype(float)
    df = df[(df.index >= pd.to_datetime("2001-10-01")) & (df.index <= pd.to_datetime("2008-10-02"))]
    print(df)
    return df


def plot_data(df):
    df.plot(title="USD Swap Curve")
    plt.show()

    df.boxplot()
    plt.title("USD Swap Rate boxplot")
    plt.show()


def pca(df):
    scaler = StandardScaler().fit(df)
    res_df = pd.DataFrame(scaler.fit_transform(df), columns=df.columns, index=df.index)
    res_df.dropna(how='any', inplace=True)
    print(f"rescaled df {res_df}")

    res_df.plot(title="rescaled data")
    plt.show()
    pc = PCA().fit(res_df)
    print(f"eigenvalues {pc.explained_variance_}, \neigenvectors {pc.components_} ")
    num_eigen = 3
    fig, axes = plt.subplots(ncols=2, figsize=(14, 4))
    Series1 = pd.Series(pc.explained_variance_ratio_[:num_eigen]).sort_values()
    Series2 = pd.Series(pc.explained_variance_ratio_[:num_eigen]).cumsum()
    Series1.plot.barh(title='Explained Variance Ratio by Top Factors', ax=axes[0])
    Series2.plot(ylim=(0, 1), ax=axes[1], title='Cumulative Explained Variance')
    plt.show()

    # compute using covariance method
    cov_matrix = res_df.cov()
    print(cov_matrix)
    plt.imshow(cov_matrix)
    plt.title("covariance matrix")
    plt.xticks(range(len(cov_matrix.columns)), cov_matrix.columns)
    plt.yticks(range(len(cov_matrix.index)), cov_matrix.index)
    plt.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    plt.show()

    # Eigendecomposition
    eigen_val, eigen_vec = np.linalg.eig(cov_matrix)
    idx = eigen_val.argsort()[::-1]
    eigen_val = eigen_val[idx]
    eigen_vec = eigen_vec[:, idx]
    pc_val = eigen_val
    pc_vec = eigen_vec.T
    pc_exp = eigen_val / np.sum(eigen_val)
    print(pc_val)
    print(pc_vec)
    print(pc_exp)
    print(cov_matrix - eigen_vec @ np.diag(eigen_val) @ eigen_vec.T)
    print(cov_matrix - pc.components_.T @ np.diag(pc.explained_variance_) @ pc.components_)

    # empirical studies reveal that more than 99% of the movement of various U.S. Treasury bond yields
    # are captured by three factors, which are often referred to as level, slope, and curvature.
    pc_main = pd.DataFrame(pc.components_[:3, :].T, index=df.columns, columns=["PC1", "PC2", "PC3"])
    eigen_main = pc.explained_variance_[:3]

    pc_main = pc_main.apply(lambda x: x * np.sqrt(eigen_main), axis=1)
    pc_main.plot(style=['s-', 'o-', '^-'], title="Principal Component")
    plt.show()

    print(f"principal component {pc_main}")
    vol = pc_main.apply(lambda x: np.sqrt((x * x).sum()), axis=1).to_frame(name="pc_vol")
    print(f"vol is {vol}")
    vol["total_vol"] = res_df.std()
    vol["PC Vol / Total Vol %"] = vol["pc_vol"] / vol["total_vol"]

    print(f"volatility {vol}")

    stat_df = pd.merge(pc_main, vol, left_index=True, right_index=True)

    pc_vol_ratio = pc_main.apply(lambda x: (x * x) / (x * x).sum(), axis=1)
    pc_vol_ratio = pc_vol_ratio.rename(columns={"PC1": "PC1_VAR%", "PC2": "PC2_VAR%", "PC3": "PC3_VAR%"})

    stat_df = pd.merge(stat_df, pc_vol_ratio, left_index=True, right_index=True)
    print(f"stat_df {stat_df}")

    # eigen factor
    pc_factor = df @ pc_main
    pc_factor.plot(title="eigenfactor values")
    plt.show()
    return pc_main, eigen_main, stat_df


if __name__ == '__main__':
    df = get_data()
    pc_main, eigen_main, stat_df = pca(df)
    print(stat_df)
    