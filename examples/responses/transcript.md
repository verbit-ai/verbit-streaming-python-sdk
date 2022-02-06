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
                "transcript": "Welcome friends, Arco vis from",
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
                "transcript": "Welcome friends, archivists from all around. Today's show in case you wanted to come over,",
                "start": 0.0,
                "end": 8.0,
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
                        "value": "all",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 3.05,
                        "end": 3.86,
                        "kind": "text",
                        "value": "around",
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
                        "value": "show",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 5.03,
                        "end": 5.09,
                        "kind": "text",
                        "value": "in",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 5.09,
                        "end": 5.63,
                        "kind": "text",
                        "value": "case",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 5.63,
                        "end": 5.99,
                        "kind": "text",
                        "value": "you",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 5.99,
                        "end": 6.59,
                        "kind": "text",
                        "value": "wanted",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 6.59,
                        "end": 6.92,
                        "kind": "text",
                        "value": "to",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 6.95,
                        "end": 7.1,
                        "kind": "text",
                        "value": "come",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 7.1,
                        "end": 7.67,
                        "kind": "text",
                        "value": "over",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    },
                    {
                        "start": 7.67,
                        "end": 7.67,
                        "kind": "punct",
                        "value": ",",
                        "speaker_id": "5a155a51-b181-4451-84f2-5f9e141aea52"
                    }
                ]
            }
        ]
    }
}
```
