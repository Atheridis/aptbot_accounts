from aptbot.bot import Bot, Message, Commands
import spacy
import re
import tools.smart_privmsg

nlp = spacy.load("en_core_web_sm")


def send_metric(bot: Bot, message: Message):
    text = ""
    ft_inch, cm = _tometric(message.value)
    for i in range(len(cm)):
        if cm[i] > 230:
            text += f"{ft_inch[i][0]:.1f}ft. and {ft_inch[i][1]:.1f}in. is {cm[i] / 100:.2f}m. | "
        elif cm[i] > 0:
            text += f"{ft_inch[i][0]:.1f}ft. and {ft_inch[i][1]:.1f}in. is {cm[i]:.1f}cm. | "
    if text:
        tools.smart_privmsg.send(bot, message, text)


def _tometric(text: str) -> tuple[list[tuple[int, int]], list[float]]:
    ft_inch: list[tuple] = []
    feet = 0
    inches = 0
    text = text.replace("-", " ")
    text = re.sub(r"([0-9]+(\.[0-9]+)?)", r"\1 ", text)
    text = re.sub(r"\s{2,}", r" ", text)
    doc = nlp(text)
    feet_was_last = False
    next_should_be_double = False
    found_single = False
    for w in doc:
        # print(w.text, w.pos_)
        if w.pos_ in {'AUX', 'VERB', 'ADP'}:
            if feet_was_last and not next_should_be_double:
                ft_inch.append((feet, 0.0))
                feet = 0
                inches = 0
        if w.like_num or w.pos_ == 'NUM':
            # index_of_previous_token = w.i - 1
            # try:
            #     prev_token = doc[index_of_previous_token]
            #     print(prev_token.lemma_)
            #     if prev_token.lemma_ != "be":
            #         continue
            # except:
            #     pass
            # if "'" in w.text:
            #     feet_and_inches = w.text.split("'")
            #     try:
            #         feet = float(feet_and_inches[0])
            #         inches = float(feet_and_inches[1])
            #     except:
            #         pass
            index_of_next_token = w.i + 1
            try:
                next_token = doc[index_of_next_token]
                if next_token.lemma_ in {"ft", "foot", "'"}:
                    if next_token.lemma_ == "'" and not next_should_be_double:
                        next_should_be_double = True
                    elif next_token.lemma_ == "'":
                        feet = 0
                        inches = 0
                        continue
                    if feet_was_last:
                        ft_inch.append((feet, 0.0))
                    feet = float(w.text)
                    feet_was_last = True
                elif next_token.lemma_ in {"inch", "\""}:
                    if next_token.lemma_ == "\"" and next_should_be_double:
                        inches = float(w.text)
                        next_should_be_double = False
                    elif next_token.lemma_ == "\"":
                        inches = 0
                    elif next_should_be_double:
                        feet = 0
                        inches = float(w.text)
                    else:
                        inches = float(w.text)
                    ft_inch.append((feet, inches))
                    feet = 0
                    inches = 0
                    feet_was_last = False
            except:
                pass
    if feet_was_last and not next_should_be_double:
        ft_inch.append((feet, 0.0))
    cm: list[float] = []
    for unit in ft_inch:
        cm.append((unit[0] * 12 + unit[1]) * 2.54)
    return (ft_inch, cm)
