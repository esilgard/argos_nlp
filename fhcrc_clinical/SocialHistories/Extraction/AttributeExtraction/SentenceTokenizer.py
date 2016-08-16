from nltk.tokenize.util import string_span_tokenize

def tokenizeSentence(sentence):

    END_PUNC = {'.','!','?'}
    MED_PUNC = {',',';',':','"'}


    toks = sentence.split()
    final_toks = list()

    #Tokenization which preserves punctuation:
    # for tok in toks:
    #     if any(punc in tok for punc in MED_PUNC):
    #         final_toks.append(tok[:-1])
    #         final_toks.append(tok[len(tok)-1])
    #     elif any(punc in tok for punc in END_PUNC) and tok==toks[len(toks)-1]: # IE we are looking at the last token in the sentence
    #         final_toks.append(tok[:-1])
    #         final_toks.append(tok[len(tok) - 1])
    #     else:
    #         final_toks.append(tok)

    # Cheap tokenization reflecting Marty's current scheme
    for tok in toks:
        tok = tok.rstrip(",.:;")
        final_toks.append(tok)
    return final_toks

def strip_sec_headers_tokenized_text(toks):
    UNWANTED_TOKS = {"SOCIAL", "HISTORY", "SUBSTANCE", "ABUSE"}

    new_toks = list()
    for tok in toks:
        if tok not in UNWANTED_TOKS:
            new_toks.append(tok)
        else:
            new_toks.append("")
    return new_toks

def span_tokenizer(sent):

    spans = string_span_tokenize(sent, " ")
    list_span_tok = list()
    for span in spans:
        list_span_tok.append((span[0], span[1], sent[span[0]:span[1]]))

    return list_span_tok