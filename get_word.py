
# coding: utf-8

# In[10]:

# Libraries used
import urllib
from urllib.request import urlopen
import pandas as pd
import sys


# In[11]:

### Reading in the corpus text
corpus_link = "https://s3.amazonaws.com/hr-testcases/482/assets/corpus.txt"


#### function: read in the corpus and process it
#### input: corpus text url
#### output: a panda dataframe with two columns: word and frequency

def get_dictionary(corpus_link):
    content = urlopen(corpus_link)
    final = [word.decode("utf-8") for line in content for word in line.split()]
    words_df = pd.DataFrame(final,columns=['message'])
    #### text preprocessing 
    #making all lowercase
    words_df['message'] = words_df['message'].apply(lambda x: x.lower())
    words_noPunc_df = pd.DataFrame(words_df['message'].apply(lambda x: ''.join([i for i in x if (i.isalpha() or (i =="-" or i =="'"))])))
    # removing the "end of corpus"
    words_noPunc_df.drop(2192024,inplace=True)
    # removing the empty spaces 
    words_noPunc_df = words_noPunc_df[words_noPunc_df['message'] != ""]
    # reseting the index
    words_noPunc_df.reset_index(drop= True, inplace=True)
    # getting the frequency of each word occurences 
    word_freq = pd.DataFrame(words_noPunc_df['message'].value_counts())
    word_freq = word_freq.reset_index()
    word_freq.columns = ['word','frequency']
    return word_freq
    


# #### Functions

# In[13]:

#### function 1: check_similarity between two words 
#### input: corpus_word,word_to_be_compared against
#### output: return -1 if no case is matched, else return 1 or 2 depending on which case
#### case 1: Deletion, case 2: Replacement, case 3: Transposition,
#### case 4: Insertion, case 5: Exactly the same

def check_similarity(corpus_word,test_word):
    # check if they are the same
    if (corpus_word == test_word):
        # case 5
        return 2
    else:
        # First to check the length of the two words
        cw_len = len(corpus_word)
        tw_len = len(test_word)
        #if the two lengths are equal --> case 2 and 3: Replacement and Transposition
        if (cw_len == tw_len):
            # create a list to store the indexes of the different characters between the two strings
            lst_count = []
            for i in range(0,cw_len):
                if (corpus_word[i] != test_word[i]):
                    # add the index to the list "lst_count"
                    lst_count.append(i)
                    
            if (len(lst_count) > 2) :
                # more than one edit distance away 
                return -1
            else:
                # len(lst_count) is either 1 or 2 
                if (len(lst_count) ==2):
                    # check for case 3 - transposition
                    diff = abs(lst_count[0] - lst_count[1])
                    # if diff = 1 it would mean they are consecutive letters 
                    if (diff == 1):
                        # check if consecutive words are swapped
                        if (check_consecutive(corpus_word,test_word,lst_count[0],lst_count[1])):
                            # case 3
                            return 1
                        else:
                            # the consecutive words are not swapped i.e different words 
                            return -1
                    else:
                        # not consecutive words
                        return -1
                else: # len(lst_count) will be 1 in this case 
                    # case 2 - replacement
                    return 1
        else:
            # check for case 1 and 4 : deletion and insertion
            # difference can only be one because of qns's restrictions
            if (abs(cw_len - tw_len) == 1):
                #count the number of characters the strings are different from each other
                incorrect_counts = 0
                # position for corpus word
                cw_pos = 0
                # position for the word being tested
                tw_pos = 0
                # check for which is the longer string 
                if (cw_len > tw_len):
                    # corpus word is longer than the given word 
                    while ((cw_pos < cw_len ) and (tw_pos < tw_len)):
                        if corpus_word[cw_pos] != test_word[tw_pos]:
                            incorrect_counts +=1
                            # check for case 1: deletion
                            # move forward in the position of the longer string
                            cw_pos +=1
                        else: 
                            # plus one for both positions
                            cw_pos+=1
                            tw_pos+=1

                    if incorrect_counts <= 1:
                        # case 1 - deletion
                        return 1
                    else:
                        # more than one edit distance away
                        return -1
                else: # tw_len > cw_len
                    while ((tw_pos < tw_len ) and (cw_pos < cw_len)):
                        # given word is longer than corpus word
                        if corpus_word[cw_pos] != test_word[tw_pos]:
                            incorrect_counts +=1
                            tw_pos +=1
                        else: # plus one for both positions
                            tw_pos+=1
                            cw_pos+=1
                    if incorrect_counts <= 1:
                        #case 4 - insertion
                        return 1
                    else:
                        return -1
            else: # falls out of one edit distance
                return -1


# In[14]:

#### boolean helper function 2 : to be used in check similarity function
#### input: input word 1 (from corpus), input word 2 (from tested word), position 1, position 2
#### output: True if consecutive and False otherwise
def check_consecutive(word1,word2,pos1,pos2):
    return ((word1[pos1] == word2[pos2]) and (word1[pos2] == word2[pos1]))    


# In[15]:

#### boolean helper function 3: to check if the word is a number or not
#### input: the word to be tested
#### output: True if numeric , else False
def check_numeric(test_word):
    return (test_word.isnumeric())


# In[16]:

#### main function to call the other functions 
#### input: corpus dictionary, word to be tested
def get_word(corpuswords_df,inputWord):
    # first is to check if the input word is numeric
    t1 = check_numeric(inputWord)
    if t1:
        return
    else:
        # not numeric
        corpuswords_df['similarity_score'] = corpuswords_df['word'].apply(lambda x: check_similarity(x,inputWord))
        corpuswords_df_1 = corpuswords_df[corpuswords_df['similarity_score'] >= 1]
        # no similar words to be found
        if len(corpuswords_df_1) == 0:
            return inputWord
        else:
            # sort based on level of similarity, frequency and then word( lexigraphically)
            sorted_df = corpuswords_df_1.sort_values(by = ['similarity_score','frequency','word'], ascending= [False,False,False])
            return sorted_df['word'].iloc[0]
    

    

# In[17]:

word_freq = get_dictionary(corpus_link)

def main():
    sys.stdout.write("Enter word:")
    strans = ''
    n = sys.stdin.readline()
    for line in range(int(n)):
        input1 = sys.stdin.readline()
        line1 = input1.strip()
        ans1 = get_word(word_freq, line1)
        print(ans1)
    


if __name__ == '__main__':
    main()



