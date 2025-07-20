import os
import json
import math

# Return the true dropout distributions for all lessons
def load_true_dropout_distribution():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    true_dropout_distribution_filename = os.path.join(current_dir, '../cip_data/true_dropout_distribution.json')
    f = open(true_dropout_distribution_filename)
    return json.load(f)

# Return the true dropout distributions for all lessons
def load_true_dropout_distribution_verbose():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    true_dropout_distribution_filename = os.path.join(current_dir, '../cip_data/true_dropout_distribution_verbose.json')
    f = open(true_dropout_distribution_filename)
    return json.load(f)

# Compute the KL divergence between two dropout distributions for a lesson
def dropout_distribution_kl_divergence(true_distribution, predicted_distribution):
    kl_divergence = 0

    # Loop over every slide in the true distribution
    for slide, p_true in true_distribution.items():
        # Only compute KL divergence if the true probability is non-zero
        if p_true > 0:
            # Get the predicted dropout for this slide
            p_predicted = predicted_distribution.get(slide, 0.0)

            # If the predicted probability is zero and 
            # the true probability is non-zero, KL is infinite
            if p_predicted == 0.0:
                return float('inf')
        
            kl_divergence += p_true * math.log(p_true / p_predicted)

    return kl_divergence

# Compute the Jensen-Shannon divergence between two dropout distributions for a lesson
def dropout_distribution_js_divergence(true_distribution, predicted_distribution):
    # Get all of the lesson slides from either distribution
    lesson_slides = set(true_distribution.keys()) | set(predicted_distribution.keys())

    # Construct the midpoint distribution m = 0.5(p + q)
    m = {}
    for slide in lesson_slides:
        p_true = true_distribution.get(slide, 0.0)
        p_pred = predicted_distribution.get(slide, 0.0)
        m[slide] = 0.5 * (p_true + p_pred)

    # Step 2: JSD = 0.5*KL(p || m) + 0.5*KL(q || m)
    kl_pm = dropout_distribution_kl_divergence(true_distribution, m)
    kl_qm = dropout_distribution_kl_divergence(predicted_distribution, m)

    js_divergence = 0.5 * kl_pm + 0.5 * kl_qm
    return js_divergence