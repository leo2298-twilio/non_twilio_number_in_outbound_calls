import pandas as pd

def analyze_and_export_missing_calls(inventory_csv, calls_csv, output_csv):
    # 1. Load the data
    inv_df = pd.read_csv(inventory_csv, low_memory=False)
    calls_df = pd.read_csv(calls_csv, low_memory=False)

    # 2. Clean the 'Count' column
    # Force everything to string, remove commas, coerce to numeric (making bad values NaN), fill NaN with 0, and cast to int.
    calls_df['Count'] = calls_df['Count'].astype(str).str.replace(',', '', regex=False)
    calls_df['Count'] = pd.to_numeric(calls_df['Count'], errors='coerce').fillna(0).astype(int)

    # 3. Clean and NORMALIZE the phone numbers
    # Convert to string, strip spaces, and remove the '+' sign if it exists
    inv_df['Did'] = inv_df['Did'].astype(str).str.strip().str.replace('+', '', regex=False)
    calls_df['Caller_Normalized'] = calls_df['Caller'].astype(str).str.strip().str.replace('+', '', regex=False)

    # 4. Identify inventory DIDs using the normalized format
    inventory_dids = set(inv_df['Did'].unique())

    # 5. Filter for callers NOT in the inventory (using the normalized column for comparison)
    not_in_inventory = calls_df[~calls_df['Caller_Normalized'].isin(inventory_dids)].copy()

    # Sort the missing ones by Count descending
    not_in_inventory = not_in_inventory.sort_values(by='Count', ascending=False)

    # Clean up the dataframe before exporting (drop the temporary normalized column)
    not_in_inventory = not_in_inventory.drop(columns=['Caller_Normalized'])

    # 6. Save the detailed breakdown to a new CSV file
    not_in_inventory.to_csv(output_csv, index=False)
    print(f"\n[SUCCESS] Exported detailed breakdown to '{output_csv}'\n")

    # 7. Compute summaries
    total_calls_missing = not_in_inventory['Count'].sum()
    total_unique_missing_callers = not_in_inventory['Caller'].nunique()

    # Print overall breakdown
    print("=== BREAKDOWN OF CALLS NOT IN INVENTORY ===")
    print(f"Total unique numbers not in inventory: {total_unique_missing_callers:,}")
    print(f"Total outbound calls from these numbers: {total_calls_missing:,}")
    print("\nTop 10 callers missing from inventory by call volume:")
    
    columns_to_show = ['Caller', 'Account Sid', 'Friendly Name', 'Count']
    print(not_in_inventory[columns_to_show].head(10).to_string(index=False))

if __name__ == "__main__":
    INVENTORY_FILE = "inventory.csv"
    CALLS_FILE = "outbound_calls.csv"
    OUTPUT_FILE = "missing_from_inventory_with_accounts.csv"
    
    analyze_and_export_missing_calls(INVENTORY_FILE, CALLS_FILE, OUTPUT_FILE)