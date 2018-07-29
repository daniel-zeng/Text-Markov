import glob, re
from numpy.random import choice

def load_texts():
	return glob.glob("dataset\\*.txt")

def has_alpha(word):
	return re.search('[a-zA-Z]', word) is not None

def has_ending(word):
	return word.find(".") != -1 or word.find("?") != -1

def only_alphanum(word):
	return re.sub(r'[^a-zA-Z0-9]', '', word)

def process_key(word1, word2):
	seperate_char = "^^"
	return (only_alphanum(word1) + seperate_char + only_alphanum(word2)).lower()

word2list = {}
word_pair_freq = {}
word2sample = {}

def process_text(file):
	with open(file) as f:
		words = f.read().split()
		prev_word2 = ""
		prev_word = "."
		for word in words:
			if not has_alpha(word):
				continue
			else:
				curr = word
				if has_ending(word):
					no_period = curr.replace(".", "").replace("?", "")
					assert len(no_period) > 0
					process_word(prev_word2, prev_word, no_period)
					process_word(prev_word, no_period, ".")
					prev_word2 = ""
					prev_word = "."
				else:
					process_word(prev_word2, prev_word, curr)
					prev_word2, prev_word = prev_word, curr
		print(len(words))

def process_word(prev2, prev1, target):
	key = process_key(prev2, prev1)
	if key not in word2list:
		word2list[key] = set()
	word2list[key].add(target)
	if (key, target) not in word_pair_freq:
		word_pair_freq[(key, target)] = 1
	else:
		word_pair_freq[(key, target)] += 1

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
def create_sampler():
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
		

def generate(start0, start, num_words = 1000):
	curr0 = start0
	curr = start
	for i in range(num_words):
		new_word = word2sample[process_key(curr0, curr)].sample()
		curr0, curr = curr, new_word

		
		if curr == ".":
			curr0 = ""
			curr = "."
			print(curr, end = "") 
		else:
			print(" " + curr, end = "") 
if __name__ == '__main__':
	for text in load_texts():
		process_text(text)
	create_sampler()
	generate("", ".")
	print()