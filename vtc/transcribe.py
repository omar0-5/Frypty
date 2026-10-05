
import json
import os

path = "transcript.json"
def gen_words(my_audio):
    """generate a dictionary (words) that contain words by start and end time"""
    import whisperx
    #imported here for efficiency purposes

    #AI PROMPT: generate the python script for whisperx that will load the transcript to the variable word 

    device = "cpu"
    #for nvidia GPUs use : device = "cuda"

    audio = whisperx.load_audio(my_audio)

    model = whisperx.load_model("small", device, compute_type="int8")
    result = model.transcribe(audio, batch_size=8 , language="en")

    #result now contains the detected language and text segments 


    #this part will split the text into word by word
    
    align_model, metadata = whisperx.load_align_model(
    language_code=result["language"], device=device
    )
    aligned = whisperx.align(
        result["segments"], align_model, metadata, audio, device
    )

    

    words = []
    for segment in aligned["segments"]:
        for w in segment["words"]:
            words.append({
                "word": w["word"],
                "start": w.get("start"),   # None when whisperx gave no time
                "end": w.get("end"),
            })

    # fill the gaps and save
    words = fill_missing_times(words)
    with open(path, "w") as f:
        json.dump(words, f, indent=2)
    return words


def transcribe(audio_path):
    """Returns the dictionary"""
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    else :
        return gen_words(audio_path)



EDGE_GUESS = 0.5  # seconds given to a stretch that has a wall on one side only

# two pointers like 
def fill_missing_times(words):
    n = len(words)
    i = 0
    while i < n:
        if words[i]["start"] is not None:
            i += 1
            continue

        # words[i] is missing. Move j forward to the first word that has a time.
        j = i
        while j < n and words[j]["start"] is None:
            j += 1

        # The stretch is words[i] ... words[j-1], so it has (j - i) words.
        # words[i-1] is the timed word before it, if i > 0.
        # words[j]   is the timed word after it,  if j < n.

        has_before = i > 0   # is there a timed word before the stretch?
        has_after = j < n    # is there a timed word after it?

        if not has_before and not has_after:
            raise ValueError("cannot fill word times: no word in the transcript has a timestamp")

        if has_before and has_after:      
            left = words[i - 1]["end"]
            right = words[j]["start"]
        elif has_after:                   
            right = words[j]["start"]
            left = max(0, right - EDGE_GUESS)
        else:                           
            left = words[i - 1]["end"]
            right = left + EDGE_GUESS

        share = (right - left) / (j - i)
        for k in range(i, j):
            words[k]["start"] = left + (k - i) * share
            words[k]["end"] = left + (k - i + 1) * share


        i = j
    return words



if __name__ == "__main__":
    import sys
    for w in transcribe(sys.argv[1]):
        print(f'{w["start"]:7.2f}  {w["end"]:7.2f}  {w["word"]}')
