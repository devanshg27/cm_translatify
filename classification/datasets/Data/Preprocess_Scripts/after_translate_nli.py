import jsonlines
import csv

test_in_path = "/home/devanshg27/nli_dataset/Data/PreTranslated_Data/NLI_EN_HI/XNLI-1.0/xnli.test.tsv"
train_in_path = "/home/devanshg27/nli_dataset/Data/PreTranslated_Data/NLI_EN_HI/XNLI-MT-1.0/multinli/multinli.train.en.tsv"
valid_in_path = "/home/devanshg27/nli_dataset/Data/PreTranslated_Data/NLI_EN_HI/XNLI-MT-1.0/multinli/multinli.valid.en.tsv"
test_out_path = "/home/devanshg27/nli_dataset/Data/Translated_Data/NLI_EN_HI/XNLI-1.0/xnli.test.tsv"
train_out_path = "/home/devanshg27/nli_dataset/Data/Translated_Data/NLI_EN_HI/XNLI-MT-1.0/multinli/multinli.train.en.tsv"
valid_out_path = "/home/devanshg27/nli_dataset/Data/Translated_Data/NLI_EN_HI/XNLI-MT-1.0/multinli/multinli.valid.en.tsv"

f_read = open("/home/devanshg27/delete/nli_after_translate.txt", "r")

def read_tsv(input_file):
	"""Reads a tab separated value file."""
	with open(input_file, "r", encoding="utf-8-sig") as f:
		return list(csv.reader(f, delimiter="\t", quotechar=None, quoting=csv.QUOTE_NONE))

def write_tsv(output_file, l):
	with open(output_file, 'w', newline='', encoding="utf-8-sig") as csvfile:
		spamwriter = csv.writer(csvfile, delimiter='\t', quotechar=None, quoting=csv.QUOTE_NONE)
		for row in l:
			spamwriter.writerow(row)

def read_line():
	return f_read.readline().strip()

def read_lines(line, line2):
	conversation = []
	for monologue in line.split('##'):
		monologue = monologue.strip()
		assert monologue != ''
		temp = monologue.split(':', 1)
		assert len(temp) == 2
		assert not any([(ch.islower() if ch.isalpha() else False) for ch in temp[0]])
		conversation.append([x.strip() for x in temp])
	for i in range(len(conversation)):
		conversation[i][1] = read_line()
	line2 = read_line()
	
	return ' ## '.join([' : '.join(monologue) for monologue in conversation]), line2
	

train_data = read_tsv(train_in_path)
for (i, line) in enumerate(train_data):
	if i%10 == 0:
		print(f"{i}/{len(train_data)} completed")
	if i == 0:
		continue
	train_data[i][0], train_data[i][1] = read_lines(train_data[i][0], train_data[i][1])
write_tsv(train_out_path, train_data)

valid_data = read_tsv(valid_in_path)
for (i, line) in enumerate(valid_data):
	if i%10 == 0:
		print(f"{i}/{len(valid_data)} completed")
	if i == 0:
		continue
	valid_data[i][0], valid_data[i][1] = read_lines(valid_data[i][0], valid_data[i][1])
write_tsv(valid_out_path, valid_data)

test_data = read_tsv(test_in_path)
for (i, line) in enumerate(test_data):
	if i%10 == 0:
		print(f"{i}/{len(test_data)} completed")
	if i == 0:
		continue
	test_data[i][6], test_data[i][7] = read_lines(test_data[i][6], test_data[i][7])
write_tsv(test_out_path, test_data)

f_read.close()