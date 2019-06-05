import os

import torch
from fastai.lm_rnn import MultiBatchRNN, SequentialRNN, LinearDecoder, load_model, Dataset, np
from fastai.text import SortSampler, DataLoader, no_grad_context
from termcolor import colored
import sentencepiece as spm


def main():
    fastai_model_path = "./blobs.bak/work/up_low50k/models/fwd_v50k_finetune_lm_enc.h5"
    sentencepiece_model_path = "./blobs.bak/work/up_low50k/tmp/sp-50k.model"
    sentencepiece_vocab_path = "./blobs.bak/work/up_low50k/tmp/sp-50k.vocab"

    def exists_or_ex(path):
        file = open(path,"r")
        file.close()
    _ = [exists_or_ex(path) for path in [fastai_model_path, sentencepiece_model_path, sentencepiece_vocab_path]]

    def highlighted(
            highlight,
            whole_text,
    ):
        return whole_text.replace(
            highlight, colored(highlight, color="green"))

    spm_processor = spm.SentencePieceProcessor()
    spm_processor.Load(sentencepiece_model_path)

    spm_processor.SetEncodeExtraOptions("bos:eos")
    spm_processor.SetDecodeExtraOptions("bos:eos")

    def get_lm(bptt, max_seq, n_tok, emb_sz, n_hid, n_layers, pad_token, bidir=False,
               tie_weights=True, qrnn=False):
        rnn_enc = MultiBatchRNN(bptt, max_seq, n_tok, emb_sz, n_hid, n_layers, pad_token=pad_token, bidir=bidir, qrnn=qrnn)
        enc = rnn_enc.encoder if tie_weights else None
        return SequentialRNN(rnn_enc, LinearDecoder(n_tok, emb_sz, 0, tie_encoder=enc))

    PAD_ID = 1
    bs = 22

    em_sz, nh, nl = 400, 1150, 4

    bptt = 5
    vs = len(spm_processor)

    lm = get_lm(bptt, 1000000, vs, em_sz, nh, nl, PAD_ID)
    load_model(lm[0], fastai_model_path)
    lm.reset()
    lm.eval()

    class LMTextDataset(Dataset):
        def __init__(self, x):
            self.x = x

        def __getitem__(self, idx):
            sentence = self.x[idx]
            return sentence[:-1], sentence[1:]

        def __len__(self):
            return len(self.x)

    def next_tokens(ids_, model, deterministic, omit_ids=[]):
        ids = [np.array(ids_)]
        test_ds = LMTextDataset(ids)
        test_samp = SortSampler(ids, key=lambda x: len(ids[x]))
        dl = DataLoader(test_ds,
                        bs,
                        transpose=True,
                        transpose_y=True,
                        num_workers=1,
                        pad_idx=PAD_ID,
                        sampler=test_samp,
                        pre_pad=False)

        tensor1 = None
        with no_grad_context():
            for (x, y) in dl:
                tensor1 = model(x)
        p = tensor1[0]

        arg = p[-1]
        r = int(
            torch.argmax(arg) if deterministic else torch.
            multinomial(p[-1].exp(), 1))

        while r in omit_ids + [ids_[-1]]:
            arg[r] = -1
            r = int(torch.argmax(arg))

        predicted_ids = [r]
        return predicted_ids

    def next_word(ss, model):
        ids = spm_processor.encode_as_ids(ss)
        return spm_processor.decode_ids(next_tokens(ids, model))

    DOT_ID = 5
    COMA_ID = 4
    COLON_ID = 44

    def next_words_best(ss, lm, n_words, deterministic=True, omit_ids=[]):
        ss_ids = spm_processor.encode_as_ids(ss)
        wip = ss
        wip_ids = ss_ids
        for i in range(n_words):
            next_ = next_tokens(wip_ids, lm, deterministic, omit_ids=omit_ids)
            wip_ids = wip_ids + next_
            wip = spm_processor.decode_ids(wip_ids)
            wip_ids = spm_processor.encode_as_ids(wip)

        return wip

    def next_words_bad(ss, lm, n_words):
        wip = ss
        for i in range(n_words):
            wip = wip + " " + next_word(wip, lm)
        return wip

    sentences = [
        "Warszawa to największe", "Te zabawki należą do",
        "Policjant przygląda się", "Na środku skrzyżowania widać",
        "Właściciel samochodu widział złodzieja z",
        "Prezydent z premierem rozmawiali wczoraj o", "Witaj drogi",
        "Gdybym wiedział wtedy dokładnie to co wiem teraz, to bym się nie",
        "Gdybym wiedziała wtedy dokładnie to co wiem teraz, to bym się nie",
        "Polscy naukowcy odkryli w Tatrach nowy gatunek istoty żywej. Zwięrzę to przypomina małpę, lecz porusza się na dwóch nogach i potrafi posługiwać się narzędziami. Przy dłuższej obserwacji okazało się, że potrafi również posługiwać się językiem polskim, a konkretnie gwarą podhalańską. Zwierzę to zostało nazwane"
    ]

    def deterministic(sentence: str, n_words=70):
        return highlighted(
            sentence, next_words_best(sentence, lm, n_words, deterministic=True))

    def non_deterministic(sentence: str, n_words=70):
        return highlighted(
            sentence, next_words_best(sentence, lm, n_words, deterministic=False))

    for sentence in sentences:
        print("")
        print(non_deterministic(sentence))


if __name__ == "__main__":
    main()


