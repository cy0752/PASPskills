"""Shared pre-fit size limits for effective-Hamiltonian fitting."""
from __future__ import annotations


def limits(fitting_data_point_count, max_retained=150):
    """Return integer limits derived from the actual fitting row count."""
    if type(fitting_data_point_count) is not int or fitting_data_point_count <= 0:
        raise ValueError("fitting_data_point_count must be a positive integer")
    if type(max_retained) is not int or max_retained <= 0:
        raise ValueError("max_retained must be a positive integer")
    parameter_limit = (3 * fitting_data_point_count) // 2
    return {
        "fitting_data_point_count": fitting_data_point_count,
        "parameter_limit": parameter_limit,
        "retained_limit": min(max_retained, parameter_limit),
    }


def check_candidate_width(feature_count, fitting_data_point_count):
    """Reject a full candidate basis that is too wide before PASP starts."""
    if type(feature_count) is not int or feature_count <= 0:
        raise ValueError("feature_count must be a positive integer")
    result = limits(fitting_data_point_count)
    result.update(candidate_feature_count=feature_count,
                 candidate_feature_limit=result["parameter_limit"])
    if feature_count > result["candidate_feature_limit"]:
        raise ValueError(
            "candidate feature count exceeds pre-fit limit: "
            f"{feature_count} > {result['candidate_feature_limit']} "
            f"for {fitting_data_point_count} fitting data points")
    return result


def check_retained_count(retained_count, fitting_data_point_count, max_retained=150):
    """Reject retained terms above the effective limit."""
    if type(retained_count) is not int or retained_count < 0:
        raise ValueError("retained_count must be a nonnegative integer")
    result = limits(fitting_data_point_count, max_retained)
    result["retained_count"] = retained_count
    if retained_count > result["retained_limit"]:
        raise ValueError(
            "retained parameter count exceeds pre-fit limit: "
            f"{retained_count} > {result['retained_limit']} "
            f"for {fitting_data_point_count} fitting data points")
    return result
