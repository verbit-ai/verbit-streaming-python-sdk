## Transcript response

Below are 3 "transcript" example responses - first, second and final response of a given utterance 
(responses between the second and the last are not shown in this example).

Note that:
- The `"is_final"` field is `true` only for the last response of that utterance, since after the final response, the current utterance is no longer updated, and a new utterance will start.
- The `"start"` field of the response remains the same for all responses of that utterance, but the `"end"` field increases with each response.
- Response `"items"` of a given response can be replaced or deleted in a succeeding response within the same utterance. 
  - For example, look at "Arco vis" in the second response, which later becomes "archivists".   

### First "transcript" response
```json
{
    "response": {
        "id": "e5ff9cc8-d5e6-4da5-aa51-bd1874f7bf49",
        "type": "transcript",
        "is_final": false,
        "is_end_of_stream": false,
        "speakers": [
            {
                "id": "5a155a51-b181-4451-84f2-5f9e141aea52",
                "label": null
            }
        ],
        "alternatives": [
            {
                "transcript": "Welcome",
                "start": 0.0,
                "end": 1.0,
                "items": [
                    {
                        "start": 0.2,
                        "end": 0.68,
                        "kind": "text",
                        "value": "Welcome",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    }
                ]
            }
        ]
    }
}
```

### Second "transcript" response
```json
{
    "response": {
        "id": "22b38e61-d09a-4a5f-a44d-a2f36e0b32d3",
        "type": "transcript",
        "is_final": false,
        "is_end_of_stream": false,
        "speakers": [
            {
                "id": "5a155a51-b181-4451-84f2-5f9e141aea52",
                "label": null
            }
        ],
        "alternatives": [
            {
                "transcript": "Welcome friends, listener Arco vis from",
                "start": 0.0,
                "end": 3.1,
                "items": [
                    {
                        "start": 0.2,
                        "end": 0.71,
                        "kind": "text",
                        "value": "Welcome",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 0.71,
                        "end": 1.25,
                        "kind": "text",
                        "value": "friends",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 1.25,
                        "end": 1.25,
                        "kind": "punct",
                        "value": ",",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 1.25,
                        "end": 1.76,
                        "kind": "text",
                        "value": "listener",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 2.03,
                        "end": 2.3,
                        "kind": "text",
                        "value": "Arco",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 2.3,
                        "end": 2.54,
                        "kind": "text",
                        "value": "vis",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 2.54,
                        "end": 2.72,
                        "kind": "text",
                        "value": "from",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    }
                ]
            }
        ]
    }
}
```

### --- More responses ---


### Final "transcript" response
```json
{
    "response": {
        "id": "5a88397c-8a61-405c-b691-1e68a511bd27",
        "type": "transcript",
        "is_final": true,
        "is_end_of_stream": false,
        "speakers": [
            {
                "id": "5a155a51-b181-4451-84f2-5f9e141aea52",
                "label": null
            }
        ],
        "alternatives": [
            {
                "transcript": "Welcome friends, listeners, archivists from future societies. Today's episode of seriously wrong starts with a warning, but this week's warning is being delivered by a very special guest, Felix bones. He runs an independent media network. He sees through all the lies and he has all the documents, take it away.",
                "start": 0.0,
                "end": 20.0,
                "items": [
                    {
                        "start": 0.2,
                        "end": 0.71,
                        "kind": "text",
                        "value": "Welcome",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 0.71,
                        "end": 1.25,
                        "kind": "text",
                        "value": "friends",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 1.25,
                        "end": 1.25,
                        "kind": "punct",
                        "value": ",",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 1.25,
                        "end": 1.88,
                        "kind": "text",
                        "value": "listeners",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 2.03,
                        "end": 2.54,
                        "kind": "text",
                        "value": "archivists",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 2.54,
                        "end": 2.72,
                        "kind": "text",
                        "value": "from",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 2.72,
                        "end": 3.05,
                        "kind": "text",
                        "value": "future",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 3.05,
                        "end": 3.86,
                        "kind": "text",
                        "value": "societies",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 3.86,
                        "end": 3.86,
                        "kind": "punct",
                        "value": ".",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 4.25,
                        "end": 4.61,
                        "kind": "text",
                        "value": "Today's",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 4.61,
                        "end": 5.03,
                        "kind": "text",
                        "value": "episode",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 5.03,
                        "end": 5.09,
                        "kind": "text",
                        "value": "of",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 5.09,
                        "end": 5.63,
                        "kind": "text",
                        "value": "seriously",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 5.63,
                        "end": 5.99,
                        "kind": "text",
                        "value": "wrong",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 5.99,
                        "end": 6.59,
                        "kind": "text",
                        "value": "starts",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 6.59,
                        "end": 6.92,
                        "kind": "text",
                        "value": "with",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 6.95,
                        "end": 7.1,
                        "kind": "text",
                        "value": "a",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 7.1,
                        "end": 7.67,
                        "kind": "text",
                        "value": "warning",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 7.67,
                        "end": 7.67,
                        "kind": "punct",
                        "value": ",",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 7.97,
                        "end": 8.39,
                        "kind": "text",
                        "value": "but",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 8.39,
                        "end": 8.66,
                        "kind": "text",
                        "value": "this",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 8.66,
                        "end": 8.96,
                        "kind": "text",
                        "value": "week's",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 8.96,
                        "end": 9.5,
                        "kind": "text",
                        "value": "warning",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 9.56,
                        "end": 9.74,
                        "kind": "text",
                        "value": "is",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 9.74,
                        "end": 9.95,
                        "kind": "text",
                        "value": "being",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 9.95,
                        "end": 10.34,
                        "kind": "text",
                        "value": "delivered",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 10.34,
                        "end": 10.55,
                        "kind": "text",
                        "value": "by",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 10.55,
                        "end": 10.64,
                        "kind": "text",
                        "value": "a",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 10.64,
                        "end": 11.12,
                        "kind": "text",
                        "value": "very",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 11.12,
                        "end": 11.57,
                        "kind": "text",
                        "value": "special",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 11.57,
                        "end": 12.11,
                        "kind": "text",
                        "value": "guest",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 12.11,
                        "end": 12.11,
                        "kind": "punct",
                        "value": ",",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 12.2,
                        "end": 12.89,
                        "kind": "text",
                        "value": "Felix",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 12.89,
                        "end": 13.61,
                        "kind": "text",
                        "value": "bones",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 13.61,
                        "end": 13.61,
                        "kind": "punct",
                        "value": ".",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 13.64,
                        "end": 13.76,
                        "kind": "text",
                        "value": "He",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 13.76,
                        "end": 14.0,
                        "kind": "text",
                        "value": "runs",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 14.0,
                        "end": 14.09,
                        "kind": "text",
                        "value": "an",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 14.09,
                        "end": 14.78,
                        "kind": "text",
                        "value": "independent",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 14.78,
                        "end": 15.2,
                        "kind": "text",
                        "value": "media",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 15.23,
                        "end": 15.89,
                        "kind": "text",
                        "value": "network",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 15.89,
                        "end": 15.89,
                        "kind": "punct",
                        "value": ".",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 15.92,
                        "end": 16.13,
                        "kind": "text",
                        "value": "He",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 16.13,
                        "end": 16.43,
                        "kind": "text",
                        "value": "sees",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 16.43,
                        "end": 16.64,
                        "kind": "text",
                        "value": "through",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 16.64,
                        "end": 16.79,
                        "kind": "text",
                        "value": "all",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 16.79,
                        "end": 16.91,
                        "kind": "text",
                        "value": "the",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 16.91,
                        "end": 17.36,
                        "kind": "text",
                        "value": "lies",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 17.36,
                        "end": 17.51,
                        "kind": "text",
                        "value": "and",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 17.51,
                        "end": 17.66,
                        "kind": "text",
                        "value": "he",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 17.66,
                        "end": 18.11,
                        "kind": "text",
                        "value": "has",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 18.14,
                        "end": 18.35,
                        "kind": "text",
                        "value": "all",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 18.35,
                        "end": 18.44,
                        "kind": "text",
                        "value": "the",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 18.44,
                        "end": 19.19,
                        "kind": "text",
                        "value": "documents",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 19.19,
                        "end": 19.19,
                        "kind": "punct",
                        "value": ",",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 19.46,
                        "end": 19.7,
                        "kind": "text",
                        "value": "take",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 19.7,
                        "end": 19.79,
                        "kind": "text",
                        "value": "it",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 19.79,
                        "end": 20.0,
                        "kind": "text",
                        "value": "away",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 20.0,
                        "end": 20.0,
                        "kind": "punct",
                        "value": ".",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    }
                ]
            }
        ]
    }
}
```
