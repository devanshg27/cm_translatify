import jsonlines
import csv
import glob

files = sorted(glob.glob('/home/devanshg27/nli_dataset/Data/PreTranslated_Data/Sentiment_EN_HI/*'))

f_read = open("/home/devanshg27/delete/sent_after_translate.txt", "r")

def read_line():
	return f_read.readline().strip()

for file in files:
	with open(file, 'r') as f_r, open(f'/home/devanshg27/nli_dataset/Data/Translated_Data/Sentiment_EN_HI/{file.split("/")[-1]}', 'w') as f_w:
		for line in f_r:
			temp = line.strip().split('\t')
			assert(len(temp) == 2)
			assert(temp[1] == temp[1].strip())
			assert(temp[0] == temp[0].strip())
			temp[0] = read_line()
			f_w.write('\t'.join(temp) + '\n')

f_read.close()