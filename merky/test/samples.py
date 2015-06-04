
from collections import OrderedDict

class Tokenset(object):
    def __init__(self, tokens, token):
        self.tokens = tokens
        self.token = token
        self.member = tokens[token]

    def __getitem__(self, key):
        return Tokenset(self.tokens, token=self.member[key])

    def __repr__(self):
        return "Tokenset(%s, token=%s)" % (repr(self.tokens), repr(self.token))

    def __str__(self):
        return self.__repr__()


D_A_NATURAL = {
    'a': 'aye!',
    'A': 'Eh.',
}
D_A_ORDERED = OrderedDict([
    (
        'A',
        'Eh.'
    ),
    (
        'a',
        'aye!'
    )
])
D_A_TOKENS = Tokenset(
    OrderedDict([
        (
            '9540eb4400be41df59a1f37ac3abb8748b7a44a5',
            OrderedDict([
                (
                    'A',
                    'Eh.'
                ),
                (
                    'a',
                    'aye!'
                )
            ])
        )
    ]),
    token='9540eb4400be41df59a1f37ac3abb8748b7a44a5'
)
D_B_NATURAL = {
    'b': 'bi',
    'B': 'Bee!',
}
D_B_ORDERED = OrderedDict([
    (
        'B',
        'Bee!'
    ),
    (
        'b',
        'bi'
    )
])
D_B_TOKENS = Tokenset(
    OrderedDict([
        (
            'fa45424f13aab9a9858927d507ccf4242a31b0ed',
            OrderedDict([
                (
                    'B',
                    'Bee!'
                ),
                (
                    'b',
                    'bi'
                )
            ])
        )
    ]),
    token='fa45424f13aab9a9858927d507ccf4242a31b0ed'
)
L_D_A_NATURAL = ({
        'a': 'aye!',
        'A': 'Eh.',
    },)
L_D_A_ORDERED = [
    OrderedDict([
        (
            'A',
            'Eh.'
        ),
        (
            'a',
            'aye!'
        )
    ])
]
L_D_A_TOKENS = Tokenset(
    OrderedDict([
        (
            '9540eb4400be41df59a1f37ac3abb8748b7a44a5',
            OrderedDict([
                (
                    'A',
                    'Eh.'
                ),
                (
                    'a',
                    'aye!'
                )
            ])
        ),
        (
            '6653a2c28a7bd9b37767ac7f677b04a25e1c687c',
            [
                '9540eb4400be41df59a1f37ac3abb8748b7a44a5'
            ]
        )
    ]),
    token='6653a2c28a7bd9b37767ac7f677b04a25e1c687c'
)
D_A_IN_B_NATURAL = {
    'b': 'b',
    'a': {
        'a': 'aye!',
        'A': 'Eh.',
    },
}
D_A_IN_B_ORDERED = OrderedDict([
    (
        'a',
        OrderedDict([
            (
                'A',
                'Eh.'
            ),
            (
                'a',
                'aye!'
            )
        ])
    ),
    (
        'b',
        'b'
    )
])
D_A_IN_B_TOKENS = Tokenset(
    OrderedDict([
        (
            'a8338b5acbc5711c1d7d747b799715046d4e7e54',
            OrderedDict([
                (
                    'a',
                    OrderedDict([
                        (
                            'A',
                            'Eh.'
                        ),
                        (
                            'a',
                            'aye!'
                        )
                    ])
                ),
                (
                    'b',
                    'b'
                )
            ])
        )
    ]),
    token='a8338b5acbc5711c1d7d747b799715046d4e7e54'
)
L_D_A_IN_B_NATURAL = ({
        'b': 'b',
        'a': {
            'a': 'aye!',
            'A': 'Eh.',
        },
    },)
L_D_A_IN_B_ORDERED = [
    OrderedDict([
        (
            'a',
            OrderedDict([
                (
                    'A',
                    'Eh.'
                ),
                (
                    'a',
                    'aye!'
                )
            ])
        ),
        (
            'b',
            'b'
        )
    ])
]
L_D_A_IN_B_TOKENS = Tokenset(
    OrderedDict([
        (
            'a8338b5acbc5711c1d7d747b799715046d4e7e54',
            OrderedDict([
                (
                    'a',
                    OrderedDict([
                        (
                            'A',
                            'Eh.'
                        ),
                        (
                            'a',
                            'aye!'
                        )
                    ])
                ),
                (
                    'b',
                    'b'
                )
            ])
        ),
        (
            '96f4ee4e2928c2e848892f27d052226638f5a993',
            [
                'a8338b5acbc5711c1d7d747b799715046d4e7e54'
            ]
        )
    ]),
    token='96f4ee4e2928c2e848892f27d052226638f5a993'
)
L_NEST_PARTIAL_NATURAL = (
    {
        'bcd': 234,
        'abc': 123,
    },
    {
        'sis': ({
                'gender': 'female',
                'name': 'sissy',
            },),
        'bro': ({
                'gender': 'male',
                'name': 'johnny',
            },),
    }
)
L_NEST_PARTIAL_ORDERED = [
    OrderedDict([
        (
            'abc',
            123
        ),
        (
            'bcd',
            234
        )
    ]),
    OrderedDict([
        (
            'bro',
            [
                OrderedDict([
                    (
                        'gender',
                        'male'
                    ),
                    (
                        'name',
                        'johnny'
                    )
                ])
            ]
        ),
        (
            'sis',
            [
                OrderedDict([
                    (
                        'gender',
                        'female'
                    ),
                    (
                        'name',
                        'sissy'
                    )
                ])
            ]
        )
    ])
]
L_NEST_PARTIAL_TOKENS = Tokenset(
    OrderedDict([
        (
            'aee8581ae8966810f38c9837eaded46e028e32e0',
            OrderedDict([
                (
                    'abc',
                    123
                ),
                (
                    'bcd',
                    234
                )
            ])
        ),
        (
            'f99c840afb82d568e3a2fe71fa0216028e9584e5',
            OrderedDict([
                (
                    'gender',
                    'female'
                ),
                (
                    'name',
                    'sissy'
                )
            ])
        ),
        (
            '549c3ea3b53130e2800871dc420406d7ba31b663',
            [
                'f99c840afb82d568e3a2fe71fa0216028e9584e5'
            ]
        ),
        (
            'faf7493ce465f477797336496b1ffb76f4112883',
            OrderedDict([
                (
                    'gender',
                    'male'
                ),
                (
                    'name',
                    'johnny'
                )
            ])
        ),
        (
            '4c9078566f2085924d2c539fdbfdc4993380c361',
            [
                'faf7493ce465f477797336496b1ffb76f4112883'
            ]
        ),
        (
            '3dab3581748db8302681180a1641bd756fa5103e',
            OrderedDict([
                (
                    'bro',
                    '4c9078566f2085924d2c539fdbfdc4993380c361'
                ),
                (
                    'sis',
                    '549c3ea3b53130e2800871dc420406d7ba31b663'
                )
            ])
        ),
        (
            'a1e0b946606be6a646717c18f3815279221aef31',
            [
                'aee8581ae8966810f38c9837eaded46e028e32e0',
                '3dab3581748db8302681180a1641bd756fa5103e'
            ]
        )
    ]),
    token='a1e0b946606be6a646717c18f3815279221aef31'
)
L_MULTI_NEST_PARTIAL_NATURAL = (
    {
        123: (
            'one',
            'two',
            'three'
        ),
    },
    {
        '1-1': (
            {
                'cracktopolis': 'methboro',
                'inner': {
                    'gar': 'bage',
                },
            },
            {
                '2-0': ({
                        'inner': {
                            'or': ('other',),
                        },
                        'some': 'thing',
                    },),
                '2-1': ({
                        'goat': 'milk',
                    },),
            }
        ),
        '1-0': (
            {
                'a dict': {
                    'a': 'b',
                },
                'a list': (
                    'a',
                    'b'
                ),
            },
            {
                '2-0': ({
                        'eins': 1,
                        'zwei': 2,
                    },),
                '2-1': ({
                        'foo': 'bar',
                        'baz': ('blah',),
                    },),
            }
        ),
    }
)
L_MULTI_NEST_PARTIAL_ORDERED = [
    OrderedDict([
        (
            123,
            [
                'one',
                'two',
                'three'
            ]
        )
    ]),
    OrderedDict([
        (
            '1-0',
            [
                OrderedDict([
                    (
                        'a dict',
                        OrderedDict([
                            (
                                'a',
                                'b'
                            )
                        ])
                    ),
                    (
                        'a list',
                        [
                            'a',
                            'b'
                        ]
                    )
                ]),
                OrderedDict([
                    (
                        '2-0',
                        [
                            OrderedDict([
                                (
                                    'eins',
                                    1
                                ),
                                (
                                    'zwei',
                                    2
                                )
                            ])
                        ]
                    ),
                    (
                        '2-1',
                        [
                            OrderedDict([
                                (
                                    'baz',
                                    [
                                        'blah'
                                    ]
                                ),
                                (
                                    'foo',
                                    'bar'
                                )
                            ])
                        ]
                    )
                ])
            ]
        ),
        (
            '1-1',
            [
                OrderedDict([
                    (
                        'cracktopolis',
                        'methboro'
                    ),
                    (
                        'inner',
                        OrderedDict([
                            (
                                'gar',
                                'bage'
                            )
                        ])
                    )
                ]),
                OrderedDict([
                    (
                        '2-0',
                        [
                            OrderedDict([
                                (
                                    'inner',
                                    OrderedDict([
                                        (
                                            'or',
                                            [
                                                'other'
                                            ]
                                        )
                                    ])
                                ),
                                (
                                    'some',
                                    'thing'
                                )
                            ])
                        ]
                    ),
                    (
                        '2-1',
                        [
                            OrderedDict([
                                (
                                    'goat',
                                    'milk'
                                )
                            ])
                        ]
                    )
                ])
            ]
        )
    ])
]
L_MULTI_NEST_PARTIAL_TOKENS = Tokenset(
    OrderedDict([
        (
            'aadc24c3821f7ce514ac253cc1c78bc4c4d44242',
            OrderedDict([
                (
                    123,
                    [
                        'one',
                        'two',
                        'three'
                    ]
                )
            ])
        ),
        (
            'dd643ff143fb7fde5abd3415257d7f6b601ebf78',
            OrderedDict([
                (
                    'cracktopolis',
                    'methboro'
                ),
                (
                    'inner',
                    OrderedDict([
                        (
                            'gar',
                            'bage'
                        )
                    ])
                )
            ])
        ),
        (
            '719551406418ad736af235b551b35e8ac411de76',
            OrderedDict([
                (
                    'inner',
                    OrderedDict([
                        (
                            'or',
                            [
                                'other'
                            ]
                        )
                    ])
                ),
                (
                    'some',
                    'thing'
                )
            ])
        ),
        (
            'f3606104f51cbf914f2fe2358f1fa9a03b15e9b7',
            [
                '719551406418ad736af235b551b35e8ac411de76'
            ]
        ),
        (
            'aaf7e45c4177a558020cc939b49f07b7b64fc69d',
            OrderedDict([
                (
                    'goat',
                    'milk'
                )
            ])
        ),
        (
            '295649e6c2c06907e2cd65feec82a43a79069be4',
            [
                'aaf7e45c4177a558020cc939b49f07b7b64fc69d'
            ]
        ),
        (
            '5ea9074149334dade7acd6cd9187a867b7d8f7be',
            OrderedDict([
                (
                    '2-0',
                    'f3606104f51cbf914f2fe2358f1fa9a03b15e9b7'
                ),
                (
                    '2-1',
                    '295649e6c2c06907e2cd65feec82a43a79069be4'
                )
            ])
        ),
        (
            'd23a63e0192db58bdae7eb2af00da31f5a7453b5',
            [
                'dd643ff143fb7fde5abd3415257d7f6b601ebf78',
                '5ea9074149334dade7acd6cd9187a867b7d8f7be'
            ]
        ),
        (
            '28dfa1f4822ac4ef9d6df9196b34af774c8742e2',
            OrderedDict([
                (
                    'a dict',
                    OrderedDict([
                        (
                            'a',
                            'b'
                        )
                    ])
                ),
                (
                    'a list',
                    [
                        'a',
                        'b'
                    ]
                )
            ])
        ),
        (
            'a412f919414e9fdc5c3b53d76f28d3d7fa6c25c3',
            OrderedDict([
                (
                    'eins',
                    1
                ),
                (
                    'zwei',
                    2
                )
            ])
        ),
        (
            'fd7e696a92d4c607b650a51338beb9422e9ebbdc',
            [
                'a412f919414e9fdc5c3b53d76f28d3d7fa6c25c3'
            ]
        ),
        (
            'd662808605e32919823792b6acc987e027161929',
            OrderedDict([
                (
                    'baz',
                    [
                        'blah'
                    ]
                ),
                (
                    'foo',
                    'bar'
                )
            ])
        ),
        (
            '22be805d898e49aa86e9507bd9e58d897fea21b4',
            [
                'd662808605e32919823792b6acc987e027161929'
            ]
        ),
        (
            'fb7f7fe1566f89275ff79da8287277d50b3e04e9',
            OrderedDict([
                (
                    '2-0',
                    'fd7e696a92d4c607b650a51338beb9422e9ebbdc'
                ),
                (
                    '2-1',
                    '22be805d898e49aa86e9507bd9e58d897fea21b4'
                )
            ])
        ),
        (
            'eafff5187530e19dd4a8585a29665a43be7d0fc0',
            [
                '28dfa1f4822ac4ef9d6df9196b34af774c8742e2',
                'fb7f7fe1566f89275ff79da8287277d50b3e04e9'
            ]
        ),
        (
            'b37a6be68c7d7ebc2ea7476006ed8f8406b1cc83',
            OrderedDict([
                (
                    '1-0',
                    'eafff5187530e19dd4a8585a29665a43be7d0fc0'
                ),
                (
                    '1-1',
                    'd23a63e0192db58bdae7eb2af00da31f5a7453b5'
                )
            ])
        ),
        (
            '17e00b960aef947bd75aedd50737d92f187d5c22',
            [
                'aadc24c3821f7ce514ac253cc1c78bc4c4d44242',
                'b37a6be68c7d7ebc2ea7476006ed8f8406b1cc83'
            ]
        )
    ]),
    token='17e00b960aef947bd75aedd50737d92f187d5c22'
)
README_FULL_TRANSFORM_NATURAL = {
    'first': (
        'a',
        'b',
        'c'
    ),
    'second': {
        'first': '1st!',
        'second': '2nd!',
    },
}
README_FULL_TRANSFORM_ORDERED = OrderedDict([
    (
        'first',
        [
            'a',
            'b',
            'c'
        ]
    ),
    (
        'second',
        OrderedDict([
            (
                'first',
                '1st!'
            ),
            (
                'second',
                '2nd!'
            )
        ])
    )
])
README_FULL_TRANSFORM_TOKENS = Tokenset(
    OrderedDict([
        (
            'e13460afb1e68af030bb9bee8344c274494661fa',
            [
                'a',
                'b',
                'c'
            ]
        ),
        (
            '555cf5554cbd46144bd01851ebb278d32d4dc538',
            OrderedDict([
                (
                    'first',
                    '1st!'
                ),
                (
                    'second',
                    '2nd!'
                )
            ])
        ),
        (
            '4c928a93cd9af338c722acfdc8daf09d186e621f',
            OrderedDict([
                (
                    'first',
                    'e13460afb1e68af030bb9bee8344c274494661fa'
                ),
                (
                    'second',
                    '555cf5554cbd46144bd01851ebb278d32d4dc538'
                )
            ])
        )
    ]),
    token='4c928a93cd9af338c722acfdc8daf09d186e621f'
)
TOKENDICT_CASE_NATURAL = {
    'd': {
        'd-1': 'D1',
        'd-0': 'D0',
        'd-2': 'D2',
    },
    'a': {
        'a-0': (
            'a0',
            'a1',
            'a2'
        ),
        'a-1': {
            'a2': 'A2',
            'a1': 'A1',
        },
    },
    'b': (
        {
            'b-0-0': 'b00',
            'b-0-1': 'b01',
        },
        (
            'b-1-0',
            'b-1-1',
            'b-1-2'
        )
    ),
    'c': (
        'c0',
        'c1',
        'c2'
    ),
}
TOKENDICT_CASE_ORDERED = OrderedDict([
    (
        'a',
        OrderedDict([
            (
                'a-0',
                [
                    'a0',
                    'a1',
                    'a2'
                ]
            ),
            (
                'a-1',
                OrderedDict([
                    (
                        'a1',
                        'A1'
                    ),
                    (
                        'a2',
                        'A2'
                    )
                ])
            )
        ])
    ),
    (
        'b',
        [
            OrderedDict([
                (
                    'b-0-0',
                    'b00'
                ),
                (
                    'b-0-1',
                    'b01'
                )
            ]),
            [
                'b-1-0',
                'b-1-1',
                'b-1-2'
            ]
        ]
    ),
    (
        'c',
        [
            'c0',
            'c1',
            'c2'
        ]
    ),
    (
        'd',
        OrderedDict([
            (
                'd-0',
                'D0'
            ),
            (
                'd-1',
                'D1'
            ),
            (
                'd-2',
                'D2'
            )
        ])
    )
])
TOKENDICT_CASE_TOKENS = Tokenset(
    OrderedDict([
        (
            '8bb070270a1914d584364658568439d52b0848f9',
            OrderedDict([
                (
                    'd-0',
                    'D0'
                ),
                (
                    'd-1',
                    'D1'
                ),
                (
                    'd-2',
                    'D2'
                )
            ])
        ),
        (
            '24f54543f37c7fa104b1e3439fc4a24e137bf030',
            OrderedDict([
                (
                    'a-0',
                    [
                        'a0',
                        'a1',
                        'a2'
                    ]
                ),
                (
                    'a-1',
                    OrderedDict([
                        (
                            'a1',
                            'A1'
                        ),
                        (
                            'a2',
                            'A2'
                        )
                    ])
                )
            ])
        ),
        (
            '653771af4fddd48a5feef9c16b38b6eb8509bf43',
            [
                OrderedDict([
                    (
                        'b-0-0',
                        'b00'
                    ),
                    (
                        'b-0-1',
                        'b01'
                    )
                ]),
                [
                    'b-1-0',
                    'b-1-1',
                    'b-1-2'
                ]
            ]
        ),
        (
            '18326bc60f1f881a599c61d052f7330d0a424e63',
            [
                'c0',
                'c1',
                'c2'
            ]
        ),
        (
            '16ca573066c45c48b507005151a9c2d4147aa6e9',
            OrderedDict([
                (
                    'a',
                    '24f54543f37c7fa104b1e3439fc4a24e137bf030'
                ),
                (
                    'b',
                    '653771af4fddd48a5feef9c16b38b6eb8509bf43'
                ),
                (
                    'c',
                    '18326bc60f1f881a599c61d052f7330d0a424e63'
                ),
                (
                    'd',
                    '8bb070270a1914d584364658568439d52b0848f9'
                )
            ])
        )
    ]),
    token='16ca573066c45c48b507005151a9c2d4147aa6e9'
)
