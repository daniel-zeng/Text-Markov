import glob, re
from numpy.random import choice

def load_texts(directory):
	return glob.glob(directory + "\\*.txt")

def has_alpha(word):
	return re.search('[a-zA-Z]', word) is not None

def has_ending(word):
	return word.find(".") != -1 or word.find("?") != -1

def only_alphanum(word):
	return re.sub(r'[^a-zA-Z0-9]', '', word)

word2list = {}
word_pair_freq = {}
word2sample = {}

def process_text(file):
	with open(file) as f:
		words = f.read().split()
		prev_word = "."
		for word in words:
			if not has_alpha(word):
				continue
			else:
				curr = word.lower()
				if has_ending(word):
					no_period = curr.replace(".", "").replace("?", "")
					process_word(prev_word, no_period)
					process_word(only_alphanum(no_period), ".")
					prev_word = "."
				else:
					process_word(prev_word, curr)
					prev_word = only_alphanum(curr)
		print(len(words))

def process_word(prev, curr):
	if prev not in word2list:
		word2list[prev] = set()
	word2list[prev].add(curr)
	if (prev, curr) not in word_pair_freq:
		word_pair_freq[(prev, curr)] = 1
	else:
		word_pair_freq[(prev, curr)] += 1

def get_prob(val, temp):
	if temp < 1e-2:
		temp = 1e-2
		
	inv = 1/temp
	if temp > 1e5:
		inv = 0

	return val ** inv

class WordSampler:
	def __init__(self, words, freqs):
		self.words = words
		self.freqs = freqs

	def sample(self):
		return choice(self.words, p=self.freqs)

temp = 1
def create_samplers():
	for key, word_set in word2list.items():
		words = []
		freqs_unnorm = []
		freq_sum = 0
		for word in sorted(word_set):
			words.append(word)
			freq_temp = get_prob(word_pair_freq[(key, word)], temp)
			freqs_unnorm.append(freq_temp)
			freq_sum += freq_temp
		freqs = [freq/freq_sum for freq in freqs_unnorm]
		word2sample[key] = WordSampler(words, freqs)
		

def generate(start, num_words = 1000):
	curr = start
	for i in range(num_words):
		curr = word2sample[curr].sample()
		if curr != ".":
			print("", curr, end = "")
			curr = only_alphanum(curr)
		else:
			print(curr, end = "")
			


if __name__ == '__main__':
	directory = "dataset"
	for text in load_texts(directory):
		process_text(text)
	create_samplers()
	start = "."
	generate(start)
	print()
