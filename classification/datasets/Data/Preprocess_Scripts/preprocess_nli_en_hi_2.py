import glob
import csv
from indicnlp.normalize.indic_normalize import DevanagariNormalizer
from sklearn.model_selection import train_test_split

test_in_path = "/home/devanshg27/nli_dataset/Data/Tagged_Data/NLI_EN_HI/XNLI-1.0/xnli.test.tsv"
train_in_path = "/home/devanshg27/nli_dataset/Data/Tagged_Data/NLI_EN_HI/XNLI-MT-1.0/multinli/multinli.train.en.tsv"

test_out_path = "/home/devanshg27/nli_dataset/Data/PreTranslated_Data/NLI_EN_HI/XNLI-1.0/xnli.test.tsv"
train_out_path = "/home/devanshg27/nli_dataset/Data/PreTranslated_Data/NLI_EN_HI/XNLI-MT-1.0/multinli/multinli.train.en.tsv"
valid_out_path = "/home/devanshg27/nli_dataset/Data/PreTranslated_Data/NLI_EN_HI/XNLI-MT-1.0/multinli/multinli.valid.en.tsv"

normalizer = DevanagariNormalizer()

def read_tsv(input_file):
	"""Reads a tab separated value file."""
	with open(input_file, "r", encoding="utf-8-sig") as f:
		return list(csv.reader(f, delimiter="\t", quotechar=None, quoting=csv.QUOTE_NONE))

def write_tsv(output_file, l):
	with open(output_file, 'w', newline='', encoding="utf-8-sig") as csvfile:
		spamwriter = csv.writer(csvfile, delimiter='\t', quotechar=None, quoting=csv.QUOTE_NONE)
		for row in l:
			spamwriter.writerow(row)

def normalized(line, line2):
	conversation = []
	for monologue in line.split('##'):
		monologue = monologue.strip()
		assert monologue != ''
		temp = monologue.split(':', 1)
		assert len(temp) == 2
		assert not any([(ch.islower() if ch.isalpha() else False) for ch in temp[0]])
		conversation.append([x.strip() for x in temp])
	for i in range(len(conversation)):
		assert(conversation[i][1] == normalizer.normalize(conversation[i][1]))
	assert(line2 == normalizer.normalize(line2))
	return ' ## '.join([' : '.join(monologue) for monologue in conversation]), line2


train_data = read_tsv(train_in_path)
for (i, line) in enumerate(train_data):
	if i%10 == 0:
		print(f"{i}/{len(train_data)} completed")
	if i == 0:
		continue
	train_data[i][0], train_data[i][1] = normalized(train_data[i][0], train_data[i][1])
train_idx, valid_idx = train_test_split(list(range(len(train_data)-1)), test_size=400, stratify=[x[2] for x in train_data[1:]], random_state=42)
write_tsv(train_out_path, [train_data[0]] + [train_data[1+idx] for idx in train_idx])
write_tsv(valid_out_path, [train_data[0]] + [train_data[1+idx] for idx in valid_idx])

test_data = read_tsv(test_in_path)
for (i, line) in enumerate(test_data):
	if i%10 == 0:
		print(f"{i}/{len(test_data)} completed")
	if i == 0:
		continue
	test_data[i][6], test_data[i][7] = normalized(test_data[i][6], test_data[i][7])
write_tsv(test_out_path, test_data)
