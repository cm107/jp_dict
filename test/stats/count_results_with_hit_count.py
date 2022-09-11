from jp_dict.parsing.combined.combined_structs import CombinedResultList

path = "/home/clayton/workspace/prj/data_keep/data/study/parse_data/filter_sorted_results.json"
results = CombinedResultList.load_from_path(path)

def printRatio(results: CombinedResultList, cumulative: bool=False):
    hit_frequencies = {}
    for result in results:
        if result.search_word_hit_count not in hit_frequencies:
            hit_frequencies[result.search_word_hit_count] = 1
        else:
            hit_frequencies[result.search_word_hit_count] += 1

    total = sum(list(hit_frequencies.values()))
    cum_freq = 0
    for hit_count in sorted(list(hit_frequencies.keys()), reverse=True):
        freq = hit_frequencies[hit_count]
        if not cumulative:
            print(f"{hit_count} Hits: Frequency {freq}/{total} ({freq/total})")
        else:
            cum_freq += freq
            print(f"{hit_count} Hits: Cumulative Frequency {cum_freq}/{total} ({cum_freq/total})")

printRatio(results, cumulative=True)