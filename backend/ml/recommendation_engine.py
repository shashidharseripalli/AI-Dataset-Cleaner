from typing import Any, Dict, List, Optional


def _add(recos: List[Dict[str, str]], name: str, reason: str) -> None:
    if any(r["algorithm"] == name for r in recos):
        return
    recos.append({"algorithm": name, "reason": reason})


def recommend_algorithms(
    dataset_type: str,
    feature_count: int,
    target_column: Optional[str],
    data_size: int,
) -> Dict[str, Any]:
    dtype = (dataset_type or "unknown").strip().lower()
    recos: List[Dict[str, str]] = []

    if not target_column and dtype in {"classification", "regression"}:
        dtype = "clustering"

    if dtype == "classification":
        _add(recos, "Logistic Regression", "Strong baseline for classification tasks.")
        _add(recos, "Random Forest", "Handles non-linear patterns and mixed features well.")
        _add(recos, "SVM", "Works well for medium-sized datasets with clear margins.")
        _add(recos, "XGBoost", "High performance on tabular classification problems.")

        if data_size > 100_000:
            _add(recos, "LightGBM", "Efficient boosting for large tabular datasets.")
        if feature_count > 200:
            _add(recos, "Linear SVM", "Scales better with high-dimensional feature spaces.")

    elif dtype == "regression":
        _add(recos, "Random Forest Regressor", "Captures non-linear relationships robustly.")
        _add(recos, "XGBoost Regressor", "Strong predictive performance on tabular regression.")
        _add(recos, "Linear Regression", "Simple, interpretable regression baseline.")
        _add(recos, "SVR", "Useful for medium-scale regression with non-linear kernels.")

        if data_size > 100_000:
            _add(recos, "LightGBM Regressor", "Fast and scalable boosting for big data.")
        if feature_count > 200:
            _add(recos, "Ridge Regression", "Stable linear baseline for many correlated features.")

    elif dtype == "clustering":
        _add(recos, "K-Means", "Fast baseline for centroid-based clustering.")
        _add(recos, "DBSCAN", "Finds arbitrarily shaped clusters and detects noise.")
        _add(recos, "Agglomerative Clustering", "Hierarchical grouping for exploratory analysis.")
        if data_size > 100_000:
            _add(recos, "MiniBatchKMeans", "Scales better for very large datasets.")

    elif dtype == "nlp":
        _add(recos, "Logistic Regression", "Strong baseline for text classification with TF-IDF.")
        _add(recos, "Linear SVM", "Often effective for sparse text features.")
        _add(recos, "XGBoost", "Useful for engineered text/tabular hybrid features.")
        if data_size > 50_000:
            _add(recos, "DistilBERT", "Transformer approach for richer text semantics at scale.")

    else:
        _add(recos, "Random Forest", "Robust default when task type is uncertain.")
        _add(recos, "XGBoost", "General-purpose strong performer for tabular data.")
        _add(recos, "SVM", "Useful fallback for structured datasets.")
        _add(recos, "Logistic Regression", "Simple baseline to sanity-check results quickly.")

    return {
        "input": {
            "dataset_type": dtype,
            "feature_count": int(feature_count),
            "target_column": target_column,
            "data_size": int(data_size),
        },
        "recommendations": recos,
    }
