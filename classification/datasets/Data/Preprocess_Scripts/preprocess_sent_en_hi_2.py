import glob
from indicnlp.normalize.indic_normalize import DevanagariNormalizer

files = glob.glob('/home/devanshg27/nli_dataset/Data/Processed_Data/Sentiment_EN_HI/Devanagari/*')

normalizer = DevanagariNormalizer()

for file in files:
	with open(file, 'r') as f_r, open(f'/home/devanshg27/nli_dataset/Data/PreTranslated_Data/Sentiment_EN_HI/{file.split("/")[-1]}', 'w') as f_w:
		for line in f_r:
			temp = line.strip().split('\t')
			assert(len(temp) == 2)
			assert(temp[1] == temp[1].strip())
			temp[0] = normalizer.normalize(temp[0].strip())
			f_w.write('\t'.join(temp) + '\n')