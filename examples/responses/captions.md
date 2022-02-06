## Captions response

Below are 3 "captions" example responses.

Note that all "captions" responses are considered final (`"is_final": true`), since "captions" responses do not update incrementally like "transcript" responses, but rather they are published sequentially.

### First "captions" response
```json
{
    "response": {
        "id": "9ab9a97c-9a21-090c-6a98-1b68e512ad32",
        "type": "captions",
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
                "transcript": "Welcome friends,",
                "start": 0.2,
                "end": 1.25,
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
                    }
                ]
            }
        ]
    }
}
```

### Second "captions" response
```json
{
    "response": {
        "id": "27f44bc9-1506-457a-8527-8e803aeb68b4",
        "type": "captions",
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
                "transcript": "archivists from all around. Today's show",
                "start": 2.03,
                "end": 5.03,
                "items": [
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
                    }
                ]
            }
        ]
    }
}
```

### Third "captions" response
```json
{
    "response": {
        "id": "14a88403c-5a64-402c-b696-1e74a517dd30",
        "type": "captions",
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
                "transcript": "in case you wanted to come over,",
                "start": 5.03,
                "end": 7.67,
                "items": [
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
