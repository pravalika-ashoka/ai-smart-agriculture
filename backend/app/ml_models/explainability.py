import numpy as np


# =========================================================
# FEATURE NAMES
# =========================================================

FEATURE_NAMES = [
    "Nitrogen",
    "Phosphorus",
    "Potassium",
    "Moisture",
    "Temperature"
]


# =========================================================
# DESCRIPTIONS
# =========================================================

FEATURE_DESCRIPTIONS = {

    "Nitrogen":
        "Nitrogen level in the soil.",

    "Phosphorus":
        "Phosphorus level in the soil.",

    "Potassium":
        "Potassium level in the soil.",

    "Moisture":
        "Amount of water present in the soil.",

    "Temperature":
        "Current soil temperature."
}


# =========================================================
# IMPACT LABEL
# =========================================================

def get_impact_label(value):

    if value >= 0.20:
        return "Very High Impact"

    elif value >= 0.10:
        return "High Impact"

    elif value >= 0.05:
        return "Moderate Impact"

    else:
        return "Low Impact"


# =========================================================
# NORMALIZE SHAP VALUES
# =========================================================

def _normalize_shap_values(shap_values):

    """
    Converts SHAP output from different SHAP versions
    into a simple 1-D importance array.

    Expected final shape:

        [feature1, feature2, ..., feature6]
    """

    # -----------------------------------------------------
    # Older SHAP versions
    # -----------------------------------------------------

    if isinstance(shap_values, list):

        array = np.asarray(
            shap_values,
            dtype=float
        )

        # Example:
        # (classes, samples, features)

        if array.ndim == 3:

            array = np.mean(
                np.abs(array),
                axis=0
            )

            return array[0]

        # Example:
        # (samples, features)

        elif array.ndim == 2:

            return np.abs(
                array[0]
            )

        else:

            return np.abs(
                array
            ).reshape(-1)


    # -----------------------------------------------------
    # Newer SHAP versions
    # -----------------------------------------------------

    array = np.asarray(
        shap_values,
        dtype=float
    )

    # Example:
    # (samples, features, classes)

    if array.ndim == 3:

        array = np.mean(
            np.abs(array),
            axis=2
        )

        return array[0]


    # Example:
    # (samples, features)

    elif array.ndim == 2:

        return np.abs(
            array[0]
        )


    # Example:
    # (features,)

    elif array.ndim == 1:

        return np.abs(
            array
        )


    # -----------------------------------------------------
    # Unexpected shape
    # -----------------------------------------------------

    else:

        return np.abs(
            array
        ).reshape(-1)


# =========================================================
# BUILD FEATURE EXPLANATION
# =========================================================

def _build_explanation(
    values,
    shap_array
):

    explanation = []

    # Make sure SHAP returned enough values
    if len(shap_array) < len(FEATURE_NAMES):

        raise ValueError(
            "SHAP returned an invalid number of feature values."
        )

    # -----------------------------------------------------
    # Create feature explanations
    # -----------------------------------------------------

    for index, value in enumerate(values):

        importance = float(
            shap_array[index]
        )

        feature_name = (
            FEATURE_NAMES[index]
        )

        explanation.append({

            "feature":
                feature_name,

            "value":
                float(value),

            "impact":
                get_impact_label(
                    importance
                ),

            "importance":
                round(
                    importance,
                    6
                ),

            "description":
                FEATURE_DESCRIPTIONS[
                    feature_name
                ]
        })

    # -----------------------------------------------------
    # Sort by importance
    # -----------------------------------------------------

    explanation.sort(

        key=lambda item:
            item["importance"],

        reverse=True
    )

    return explanation


# =========================================================
# FALLBACK EXPLANATION
# =========================================================

def _fallback_explanation(values):

    explanation = []

    for index, value in enumerate(values):

        feature_name = (
            FEATURE_NAMES[index]
        )

        explanation.append({

            "feature":
                feature_name,

            "value":
                float(value),

            "impact":
                "Available",

            "importance":
                0,

            "description":
                FEATURE_DESCRIPTIONS[
                    feature_name
                ]
        })

    return {

        "method":
            "Feature-based explanation",

        "features":
            explanation
    }


# =========================================================
# GENERATE EXPLANATION
# =========================================================

def generate_explanation(
    features,
    model=None
):

    # =====================================================
    # VALIDATE INPUT
    # =====================================================

    try:

        if features is None:

            raise ValueError(
                "Features cannot be None."
            )

        if len(features) == 0:

            raise ValueError(
                "Features cannot be empty."
            )

        values = np.asarray(
            features[0],
            dtype=float
        )

    except Exception as error:

        raise ValueError(
            f"Invalid soil feature data: {error}"
        )


    # =====================================================
    # VALIDATE FEATURE COUNT
    # =====================================================

    if len(values) != len(
        FEATURE_NAMES
    ):

        raise ValueError(
            "Invalid number of soil features."
        )


    # =====================================================
    # SHAP EXPLANATION
    # =====================================================

    if model is not None:

        try:

            # ------------------------------------------------
            # IMPORTANT:
            # SHAP is imported only when needed.
            #
            # This reduces startup memory usage on Render.
            # ------------------------------------------------

            import shap


            # ------------------------------------------------
            # Create TreeExplainer only for this request.
            #
            # It is NOT stored globally.
            # ------------------------------------------------

            explainer = (
                shap.TreeExplainer(
                    model
                )
            )


            # ------------------------------------------------
            # Calculate SHAP values
            # ------------------------------------------------

            shap_values = (
                explainer.shap_values(
                    values.reshape(1, -1)
                )
            )


            # ------------------------------------------------
            # Normalize output from different SHAP versions
            # ------------------------------------------------

            shap_array = (
                _normalize_shap_values(
                    shap_values
                )
            )


            # ------------------------------------------------
            # Validate SHAP output
            # ------------------------------------------------

            if len(shap_array) != len(
                FEATURE_NAMES
            ):

                raise ValueError(
                    "SHAP output does not match "
                    "the number of soil features."
                )


            # ------------------------------------------------
            # Build explanation
            # ------------------------------------------------

            explanation = (
                _build_explanation(
                    values,
                    shap_array
                )
            )


            # ------------------------------------------------
            # Return JSON-safe result
            # ------------------------------------------------

            return {

                "method":
                    "SHAP - Random Forest",

                "features":
                    explanation
            }


        except Exception as error:

            print(
                "SHAP explanation error:",
                error
            )

            # ------------------------------------------------
            # IMPORTANT:
            # Do NOT fail the complete soil analysis
            # just because SHAP failed.
            # ------------------------------------------------

            return _fallback_explanation(
                values
            )


    # =====================================================
    # FALLBACK WHEN MODEL IS NOT PROVIDED
    # =====================================================

    return _fallback_explanation(
        values
    )