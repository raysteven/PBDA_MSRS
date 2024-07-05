import pandas as pd
import numpy as np

def createNestedDict(df, key_columns, value_column, special_case=None):
    nested_dict = {}

    for index, row in df.iterrows():
        current_level = nested_dict

        for key_column in key_columns[:-1]:
            key_value = row[key_column]

            if key_value not in current_level:
                current_level[key_value] = {}
            
            current_level = current_level[key_value]

        final_key = row[key_columns[-1]]

        if special_case and callable(special_case):
            current_level[final_key] = special_case(row[value_column])
        else:
            current_level[final_key] = row[value_column]

    return nested_dict

def process_AGTCDI_equivalent(value):
    return {'A': value[0], 'B': value[2]}


def createSampleGenotype(AB, AGTCDI, column_rename=None):
    sample_genotype = AB
    AGTCDI_equivalent = AGTCDI
    ##SUBSTITUTE GENOTYPE WITH AGTCDI EQUIVALENT

    for sample_prodiaId in sample_genotype.columns:
        for locus in sample_genotype.index:
            substituted_genotype = ''
            
            if sample_genotype.at[locus, sample_prodiaId] == '--':
                sample_genotype.at[locus, sample_prodiaId] = "NC"
            else:
                try:
                    for i in range(len(sample_genotype.at[locus, sample_prodiaId])):
                        AGTCDI_equivalent_call_key = sample_genotype.at[locus, sample_prodiaId][i]
                        substituted_genotype += AGTCDI_equivalent[locus][str(AGTCDI_equivalent_call_key)]

                    sample_genotype.at[locus, sample_prodiaId] = substituted_genotype
                
                except:
                    sample_genotype.at[locus, sample_prodiaId] = np.nan
                    continue

    #drop row with null values
    sample_genotype = sample_genotype.dropna()

    if column_rename != None:
        # Rename columns using the dictionary
        sample_genotype = sample_genotype.rename(columns=column_rename)
        sample_genotype.rename(columns=lambda x: x.replace(' ', '_'), inplace=True)

    return sample_genotype

def generate_variant_rules(alleles, current_genotype=''):
    if not alleles:
        return [current_genotype]

    first_gene_alleles = alleles[0]
    remaining_genes = alleles[1:]
    genotypes = []

    for allele in first_gene_alleles:
        next_genotype = current_genotype + '/' + allele if current_genotype else allele
        genotypes.extend(generate_variant_rules(remaining_genes, next_genotype))

    return genotypes

def calculate_population_frequency(input_dict):
    total_population = sum(input_dict.values())

    result_dict = {}

    # Iterate through denominators (10, 100, and 1000)
    for denominator in [10, 100, 1000]:
        frequencies = {key: round(value / total_population, (int(len(str(denominator))-1))) for key, value in input_dict.items()}
  
        print(frequencies)
        # Create a DataFrame from the frequencies
        df = pd.DataFrame(list(frequencies.items()), columns=['Key', 'Frequency'])
        print(df)
        # Add a column for the adjusted population count
        df[f'Population_{denominator}'] = round((df['Frequency'] * denominator).astype(int))

        # Format the output as "x in y"
        df[f'Denominator_{denominator}'] = df.apply(lambda row: f"{row[f'Population_{denominator}']} in {denominator}", axis=1)

        result_dict[denominator] = df[['Key', f'Denominator_{denominator}']]

    # Merge DataFrames on the 'Key' column
    final_result = result_dict[10]
    for denominator, df in result_dict.items():
        if denominator != 10:
            final_result = pd.merge(final_result, df, on='Key')

    return final_result

if __name__ == "__main__":
    pass