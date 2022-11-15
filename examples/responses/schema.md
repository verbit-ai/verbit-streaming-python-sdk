## Response schema 

Responses returned by Verbit's Streaming Speech Recognition services have the following schema:

```
{
    "response": {
        "id": string (UUID),
        "type": "transcript" | "captions",
        "start": float,
        "end": float,
        "start_pts": float,
        "start_epoch": float,
        "is_final": boolean,
        "is_end_of_stream": boolean,
        "speakers": [
            {
                "id": string (UUID),
                "label": string | null
            }
        ],
        "alternatives": [
            {
                "transcript": string,
                "start": float,
                "end": float,
                "start_pts": float,
                "start_epoch": float,
                "items": [
                    {
                        "start": float,
                        "end": float,
                        "kind": "text" | "punct",
                        "value": string,
                        "speaker_id": string (UUID)
                    }
                ]
            }
        ]
    }
}
```

### Fields description
- `"response"` - The root element in the response JSON
  - `"id"` - A unique identifier of the response (UUID)
  - `"type"` - The response type. Can be either "transcript" or "captions" (See explanation in [README.md](https://github.com/verbit-ai/verbit-streaming-python-sdk/blob/main/README.md#responses)).
  - `"start"` - The start time of the utterance. Measured in seconds from the beginning of the media stream.
  - `"end"` - The (current) end time of the utterance. Measured in seconds from the beginning of the media stream.
  - `"start_pts"` - The pts value corresponding to the `"start"` of the response, as received from the input media stream. Measured in seconds.
    - Note: if the input media stream doesn't provide pts values, this field will have the same value as `"start"`.
  - `"start_epoch"` - The epoch timestamp at which the media corresponding to the `"start"` of the response was received.
  - `"is_final"` - A boolean denoting whether the response is the final one for the utterance (See explanation in [README.md](https://github.com/verbit-ai/verbit-streaming-python-sdk/blob/main/README.md#responses)). For a "captions" response, this is always set to `"true"`, since captions are not incrementally updated (thus, each "captions" response is final).
  - `"is_end_of_stream"` - A boolean denoting whether the response is the last one for the entire media stream
  - `"speakers"` - A list of objects representing speakers in the media stream, as identified by the speech recognition service. 
    - `"id"` - A unique identifier of the speaker (UUID)
    - `"label"` - A string representing the speaker. Only available in sessions with human transcribers in the loop. This field is set to `null` by default.
  - `"alternatives"` - A list of alternative transcription hypotheses. At least one alternative is always returned.
    - `"transcript"` - A textual representation of the alternative in the current response.
    - `"start"` - Same as `["response"]["start"]`.
    - `"end"` - Same as `["response"]["end"]`.
    - `"start_pts"` - Same as `["response"]["start_pts"]`.
    - `"start_epoch"` - Same as `["response"]["start_epoch"]`.
    - `"items"` - A list containing textual items (words and punctuation marks) and their timings.
      - `"start"` - The start time of the item. Measured in seconds from the beginning of the media stream.
      - `"end"` - The end time of the item. Measured in seconds from the beginning of the media stream.
      - `"kind"` - The item kind. Can be either "text" or "punct" (a punctuation mark).
      - `"value"` - The item textual value
      - `"speaker_id"` - The unique identifier of the speaker that this item is associated with. Corresponds with an `"id"` of one of the speakers in the `"speakers"` field. 