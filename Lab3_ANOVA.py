import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats


def process_and_test_lab3(file_path):
    """
    Lab 3: ANOVA Test Module
    This module performs data cleaning, quantile binning for GDP,
    and executes the One-Way ANOVA test.
    """

    # ==========================================
    # Step 1: Environment Setup and Robustness Checks
    # ==========================================
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Dataset file not found: {file_path}. Please ensure it is in the same directory as the script."
        )

    try:
        # ==========================================
        # Step 2: Data Loading and Core Feature Extraction
        # ==========================================
        print("Loading and extracting the core dataset for ANOVA...")
        df = pd.read_csv(file_path)

        core_columns = [
            'country', 'year', 'iso_code', 'gdp', 'renewables_share_energy'
        ]
        df_subset = df[[col for col in core_columns if col in df.columns]].copy()

        # ==========================================
        # Step 3: Data Cleaning (Consistent with Lab 2)
        # ==========================================
        df_cleaned = df_subset.dropna(subset=['iso_code']).copy()
        df_cleaned = df_cleaned[df_cleaned['year'] >= 2000]
        df_cleaned = df_cleaned.dropna(subset=['gdp', 'renewables_share_energy'])

        # ==========================================
        # Step 4: Baseline Year Selection & Feature Engineering
        # ==========================================
        base_year = 2019
        if base_year not in df_cleaned['year'].values:
            base_year = df_cleaned['year'].max()

        # Extract cross-sectional data for the specific year
        df_base = df_cleaned[df_cleaned['year'] == base_year].copy()
        print(f"Applying cross-sectional data for the baseline year: {base_year}")

        # Quantile Binning: Split GDP into 3 equal-sized groups
        df_base['gdp_group'] = pd.qcut(
            df_base['gdp'],
            q=3,
            labels=['Low GDP', 'Medium GDP', 'High GDP']
        )

        # ==========================================
        # Step 5: Perform One-Way ANOVA
        # ==========================================
        group_low = df_base[df_base['gdp_group'] == 'Low GDP']['renewables_share_energy']
        group_mid = df_base[df_base['gdp_group'] == 'Medium GDP']['renewables_share_energy']
        group_high = df_base[df_base['gdp_group'] == 'High GDP']['renewables_share_energy']

        print("\nExecuting One-Way ANOVA Test...")
        f_stat, p_value = stats.f_oneway(group_low, group_mid, group_high)

        # Print detailed statistical results
        print("-" * 40)
        print("=== Statistical Output ===")
        print(f"F-Statistic: {f_stat:.4f}")
        print(f"P-Value:     {p_value:.4e}")

        if p_value < 0.05:
            print("Conclusion:  Reject the Null Hypothesis (Significant difference found).")
        else:
            print("Conclusion:  Fail to reject the Null Hypothesis (No significant difference).")
        print("-" * 40)

        return df_base

    except Exception as e:
        print(f"An error occurred during data processing: {e}")
        return None


def plot_lab3_boxplot(df_base):
    """
    Plot and save the Boxplot for Lab 3 ANOVA visualization.
    """
    sns.set(style="whitegrid")
    output_dir = "figures"
    os.makedirs(output_dir, exist_ok=True)

    # ==========================================
    # Figure 4 (Lab 3): Boxplot of Energy Share by GDP Group
    # ==========================================
    plt.figure(figsize=(9, 6))

    sns.boxplot(
        data=df_base,
        x="gdp_group",
        y="renewables_share_energy",
        hue="gdp_group",
        legend=False,
        palette="Set2",
        order=['Low GDP', 'Medium GDP', 'High GDP'],
        showmeans=True,  # Display the mean as an indicator (useful for ANOVA)
        meanprops={"marker": "o",
                   "markerfacecolor": "white",
                   "markeredgecolor": "black",
                   "markersize": "8"}
    )

    plt.title("Figure 4. Renewables Share of Energy by GDP Group (Baseline Year)", fontsize=14)
    plt.xlabel("GDP Income Group", fontsize=12)
    plt.ylabel("Renewables Share of Energy (%)", fontsize=12)
    plt.tight_layout()

    save_path = os.path.join(output_dir, "figure4_anova_boxplot.png")
    plt.savefig(save_path, dpi=300)
    print(f"\nLab 3 visualization saved successfully: '{save_path}'")
    plt.show()


# --- Main Execution ---
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    target_file = os.path.join(current_dir, "worldenergy.csv")

    # Run processing and stats
    df_anova_ready = process_and_test_lab3(target_file)

    # Generate Visualization if processing was successful
    if df_anova_ready is not None:
        plot_lab3_boxplot(df_anova_ready)