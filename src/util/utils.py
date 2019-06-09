def get_kana_maps(text: str, furigana_parts: list, okurigana_parts: list) -> list:
    kana_maps = []
    for character in text:
        if len(okurigana_parts) == 0 or character != okurigana_parts[0]:
            if len(furigana_parts) > 0:
                kana_map = {'written_form': character, 'reading': furigana_parts[0]}
                furigana_parts = furigana_parts[1:]
            else:
                kana_map = {'written_form': character, 'reading': ''}
            kana_maps.append(kana_map)
        else:
            kana_map = {'written_form': character, 'reading': okurigana_parts[0]}
            okurigana_parts = okurigana_parts[1:]
            kana_maps.append(kana_map)
    return kana_maps