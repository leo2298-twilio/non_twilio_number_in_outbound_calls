import pandas as pd

def analyze_and_export_missing_calls(inventory_csv, calls_csv, output_csv):
    # 1. Load the data
    inv_df = pd.read_csv(inventory_csv)
    calls_df = pd.read_csv(calls_csv)

    # 2. Clean the 'Count' column
    # First, fill any NaN/empty values with '0'
    calls_df['Count'] = calls_df['Count'].fillna('0')
    
    # Then remove commas and convert to integer
    if calls_df['Count'].dtype == 'O': # Check if it's object/string type
        calls_df['Count'] = calls_df['Count'].astype(str).str.replace(',', '').astype(int)
    else:
        # If it's already numeric but has NaNs, fillna(0) makes them floats, so we cast to int
        calls_df['Count'] = calls_df['Count'].astype(int)

    # Clean the phone numbers (strip spaces)
    inv_df['Did'] = inv_df['Did'].astype(str).str.strip()
    calls_df['Caller'] = calls_df['Caller'].astype(str).str.strip()

    # 3. Identify inventory DIDs
    inventory_dids = set(inv_df['Did'].unique())

    # 4. Filter for callers NOT in the inventory
    not_in_inventory = calls_df[~calls_df['Caller'].isin(inventory_dids)].copy()

    # Sort the missing ones by Count descending
    not_in_inventory = not_in_inventory.sort_values(by='Count', ascending=False)

    # 5. Save the detailed breakdown to a new CSV file
    not_in_inventory.to_csv(output_csv, index=False)
    print(f"\n[SUCCESS] Exported detailed breakdown to '{output_csv}'\n")

    # 6. Compute summaries
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