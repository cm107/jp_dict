jpdict history print-entries \
--value "lambda entry: entry['title'].split(' - ')[0]" \
--get "lambda entry: entry['url'].startswith('https://jisho.org/search/')" \
--get "lambda value: '#' not in value" \
--sort "lambda entry: entry['time_usec']" \
--tail 50
