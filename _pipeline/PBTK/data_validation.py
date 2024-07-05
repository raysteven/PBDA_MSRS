import pandas as pd
import numpy as np

def data_validation(A, B):
    # Create a union of both indices and columns
    index_union = A.index.union(B.index)
    columns_union = A.columns.union(B.columns)

    # Create an empty dataframe C with the union of indices and columns
    C = pd.DataFrame(index=index_union, columns=columns_union)

    # Iterate through each cell in A and B
    for col in columns_union:
        for idx in index_union:
            val_A = A.at[idx, col] if (idx in A.index and col in A.columns) else None
            val_B = B.at[idx, col] if (idx in B.index and col in B.columns) else None

            try:
                # Compare values and populate C accordingly
                #NE == Not Equal
                if pd.isnull(val_A) & pd.isnull(val_B):
                    C.at[idx, col] = "<both null>"
                elif pd.isnull(val_A):
                    C.at[idx, col] = f"<NE> null || {val_B}"
                elif pd.isnull(val_B):
                    C.at[idx, col] = f"<NE> {val_A} || null"
                elif val_A == val_B:
                    C.at[idx, col] = f"<OK>{val_A}"
                else:
                    C.at[idx, col] = f"<NE> {val_A} || {val_B}"
            except Exception as e:
                # Handle any exceptions
                C.at[idx, col] = f"<error> {str(e)}"

    # Return the resulting dataframe C
    return C

def data_merge(A, B, select_main):
    # Create a union of both indices and columns
    index_union = A.index.union(B.index)
    columns_union = A.columns.union(B.columns)

    # Create an empty dataframe C with the union of indices and columns
    C = pd.DataFrame(index=index_union, columns=columns_union)


    # Iterate through each cell in A and B
    for col in columns_union:
        for idx in index_union:
            val_A = A.at[idx, col] if (idx in A.index and col in A.columns) else None
            val_B = B.at[idx, col] if (idx in B.index and col in B.columns) else None

            if select_main == 'A':
                val_main = val_A
            elif select_main == 'B':
                val_main = val_B
            else:
                print('Specify only A or B!')

            try:
                # Compare values and populate C accordingly
                if pd.isnull(val_A) & pd.isnull(val_B):
                    C.at[idx, col] = ""
                elif pd.isnull(val_A):
                    C.at[idx, col] = f"{val_B}"
                elif pd.isnull(val_B):
                    C.at[idx, col] = f"{val_A}"
                elif val_A == val_B:
                    C.at[idx, col] = f"{val_main}"
                else:
                    C.at[idx, col] = f"{val_main}"
            except Exception as e:
                # Handle any exceptions
                C.at[idx, col] = f"<error> {str(e)}"

    # Return the resulting dataframe C
    return C


def data_validation_backup(A, B):

    # Create an empty dataframe C with the union of indices from A and B
    index_union = A.index.union(B.index)
    C = pd.DataFrame(index=index_union, columns=A.columns)

    # Iterate through each cell in A and B
    for col in A.columns:
        for idx in index_union:
            val_A = A.at[idx, col] if idx in A.index else None
            val_B = B.at[idx, col] if idx in B.index else None

            try:

                # Compare values and populate C accordingly
                if pd.isnull(val_A) & pd.isnull(val_B):
                    C.at[idx, col] = "<both null>"
                elif pd.isnull(val_A):
                    C.at[idx, col] = f"<not_ok> null || {val_B}"
                elif pd.isnull(val_B):
                    C.at[idx, col] = f"<not_ok> {val_A} || null"
                elif val_A == val_B:
                    C.at[idx, col] = f"{val_A}"
                else:
                    C.at[idx, col] = f"<not_ok> {val_A} || {val_B}"
            except:
                # Compare values and populate C accordingly
                if val_A & val_B == np.nan:
                    C.at[idx, col] = "<not_ok>"
                elif val_A == np.nan:
                    C.at[idx, col] = f"<not_ok> null || {val_B}"
                elif val_B == np.nan:
                    C.at[idx, col] = f"<not_ok> {val_A} || null"
                elif val_A == val_B:
                    C.at[idx, col] = f"{val_A}"
                else:
                    C.at[idx, col] = f"<not_ok> {val_A} || {val_B}"

    # Print the resulting dataframe C
    return C

def data_validation2(A, B):
    # Identify common indices
    common_indices = A.index.union(B.index)

    # Create dataframes with common indices
    A_common = A.loc[common_indices]
    B_common = B.loc[common_indices]

    # Initialize C with "not_ok" values
    C = pd.DataFrame(index=common_indices, columns=A.columns, data="<not_ok>")

    # Create a mask for matching values
    match_mask = A_common.eq(B_common)

    # Update C for non-matching values
    C[~match_mask] = (
        "<not_ok> " + A_common[~match_mask].astype(str) + " || " + B_common[~match_mask].astype(str)
    )

    # Update C for matching values
    C[match_mask] = A_common[match_mask].astype(str)

    return C




if __name__ == "__main__":
    pass