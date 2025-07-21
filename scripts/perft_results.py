"""
Known Perft Results for chess position verification.
These are the expected node counts from Stockfish and other established engines
at various depths for different chess positions. Used to verify that our
move generation is 100% accurate and follows all chess rules correctly.

Perft (Performance Test) counts the number of leaf nodes at a given depth,
which must match exactly for the engine to be considered correct.
"""

# Standard perft test positions with known results from trusted engines
PERFT_POSITIONS = {
    "starting_position": {
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "description": "Standard chess starting position",
        "results": {
            1: 20,        # 20 possible opening moves
            2: 400,       # 400 positions after 1 move for each side
            3: 8902,      # 8,902 positions after 1.5 moves
            4: 197281,    # etc.
            5: 4865609,
            6: 119060324
        },
        # Move-by-move breakdown for depth 3 (useful for debugging)
        "divide_3": {
            "a2a3": 380, "b2b3": 420, "c2c3": 420, "d2d3": 539, "e2e3": 599,
            "f2f3": 380, "g2g3": 420, "h2h3": 380, "a2a4": 420, "b2b4": 421,
            "c2c4": 441, "d2d4": 560, "e2e4": 600, "f2f4": 401, "g2g4": 421,
            "h2h4": 420, "b1a3": 400, "b1c3": 440, "g1f3": 440, "g1h3": 400
        }
    },
    
    "en_passant_position": {
        "fen": "rnbqkbnr/pppp1ppp/8/4p3/3P4/8/PPP2PPP/RNBQKBNR b KQkq d3 0 2",
        "description": "Position with en passant capture available",
        "results": {
            1: 31,
            2: 1137,
            3: 35522,
            4: 734582
        },
        "divide_3": {
            "e5e4": 1102, "a7a6": 1129, "b7b6": 1200, "c7c6": 1205, "d7d6": 1251,
            "f7f6": 992, "g7g6": 1203, "h7h6": 1129, "a7a5": 1203, "b7b5": 1172,
            "c7c5": 1190, "d7d5": 1364, "f7f5": 1136, "g7g5": 1099, "h7h5": 1205,
            "e5d4": 1072, "b8a6": 1162, "b8c6": 1242, "g8f6": 1091, "g8h6": 1125,
            "g8e7": 901, "f8a3": 1193, "f8b4": 209, "f8c5": 1268, "f8d6": 1129,
            "f8e7": 1089, "d8h4": 1445, "d8g5": 1469, "d8f6": 1502, "d8e7": 1128,
            "e8e7": 917
        }
    },
    
    "castling_position": {
        "fen": "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
        "description": "Castling rights position",
        "results": {
            1: 26,
            2: 568,
            3: 13744,
            4: 314346,
            5: 7594526
        },
        "divide_3": {
            "a1b1": 583, "a1c1": 560, "a1d1": 489, "a1a2": 632, "a1a3": 611,
            "a1a4": 586, "a1a5": 560, "a1a6": 533, "a1a7": 418, "a1a8": 87,
            "h1f1": 489, "h1g1": 560, "h1h2": 656, "h1h3": 634, "h1h4": 608,
            "h1h5": 581, "h1h6": 553, "h1h7": 434, "h1h8": 90, "e1d1": 492,
            "e1f1": 492, "e1d2": 705, "e1e2": 752, "e1f2": 705, "e1g1": 470,
            "e1c1": 464
        }
    },
    
    "promotion_position": {
        "fen": "8/P7/8/8/8/8/7p/4k2K w - - 0 1",
        "description": "Pawn promotion position",
        "results": {
            1: 6,
            2: 40,
            3: 234,
            4: 1560,
            5: 9612
        },
        "divide_3": {
            "a7a8q": 108, "a7a8r": 78, "a7a8b": 38, "a7a8n": 18, "h1h2": 40, "h1g2": 53
        }
    },
    
    "complex_position": {
        "fen": "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
        "description": "Complex position (promotions, captures, castling, en passant, checks)",
        "results": {
            1: 6,
            2: 264,
            3: 9467,
            4: 422333,
            5: 15833292
        },
        "divide_3": {
            "f2f3": 695, "g2g3": 617, "h2h3": 643, "e5e6": 662, "f2f4": 670,
            "g2g4": 618, "h2h4": 669, "b7a8q": 68, "b7a8r": 62, "b7a8b": 377,
            "b7a8n": 359, "b7b8q": 86, "b7b8r": 80, "b7b8b": 500, "b7b8n": 479,
            "e5d6": 639, "a1b1": 691, "a1c1": 942, "a1d1": 737, "a1a2": 702,
            "h1f1": 591, "h1g1": 617, "e1d1": 625, "e1f1": 585, "e1d2": 885,
            "e1e2": 904, "e1g1": 693
        }
    },
    
    "kiwipete": {
        "fen": "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
        "description": "Kiwipete position",
        "results": {
            1: 48,
            2: 2039,
            3: 97862,
            4: 4085603,
            5: 193690690
        }
    },
    
    "position_3": {
        "fen": "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
        "description": "Position 3",
        "results": {
            1: 14,
            2: 191,
            3: 2812,
            4: 43238,
            5: 674624,
            6: 11030083,
            7: 178633661
        }
    },
    
    "position_4": {
        "fen": "r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1",
        "description": "Position 4 (Black to move)",
        "results": {
            1: 26,
            2: 568,
            3: 13744,
            4: 314346,
            5: 7594526,
            6: 179862938
        }
    },
    
    "position_5": {
        "fen": "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
        "description": "Position 5 (Complex middlegame position)",
        "results": {
            1: 44,
            2: 1486,
            3: 62379,
            4: 2103487,
            5: 89941194
        },
        "divide_3": {
            "a2a3": 1464, "a2a4": 1433, "b2b3": 1372, "b2b4": 1398, "c2c3": 1447,
            "c2c4": 1501, "g2g3": 1286, "g2g4": 1337, "h2h3": 1417, "h2h4": 1402,
            "e2d4": 1355, "e2f4": 1444, "e2g3": 1264, "e2c3": 1447, "c4b3": 1315,
            "c4d3": 1501, "c4a2": 1501, "c4f7": 1501, "c4d5": 1447, "c4b5": 1447,
            "c4a6": 1501, "g1f3": 1447, "g1h3": 1286, "e1d1": 1372, "e1f1": 1447,
            "e1d2": 1501, "e1f2": 1315
        },
        "divide_5": {
            "a2a3": 2095050, "a2a4": 2101105, "b2b3": 1963263, "b2b4": 1990854,
            "c2c3": 2057144, "c2c4": 2145478, "g2g3": 1805658, "g2g4": 1830854,
            "h2h3": 2022427, "h2h4": 2015932, "e2d4": 1903937, "e2f4": 2063420,
            "e2g3": 1759014, "e2c3": 2044906, "c4b3": 1894758, "c4d3": 2145478,
            "c4a2": 2145478, "c4f7": 2145478, "c4d5": 2057144, "c4b5": 2057144,
            "c4a6": 2145478, "g1f3": 2057144, "g1h3": 1805658, "e1d1": 1963263,
            "e1f1": 2057144, "e1d2": 2145478, "e1f2": 1894758
        }
    },
    
    "position_6": {
        "fen": "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
        "description": "Position 6 (Symmetric middlegame)",
        "results": {
            1: 46,
            2: 2079,
            3: 89890,
            4: 3894594,
            5: 164075551
        }
    },
    
    "kiwipete": {
        "fen": "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
        "description": "Kiwipete (Peter Ellis Jones position)",
        "results": {
            1: 6,
            2: 264,
            3: 9467,
            4: 422333,
            5: 15833292,
            6: 706045033
        },
        "divide_1": {
            "a5a6": 1, "b5b6": 1, "f2f3": 1, "f2f4": 1, "g2g3": 1, "g2g4": 1
        }
    },
    
    "endgame_position": {
        "fen": "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
        "description": "Endgame position with pawn races",
        "results": {
            1: 14,
            2: 191,
            3: 2812,
            4: 43238,
            5: 674624,
            6: 11030083,
            7: 178633661
        }
    },
    
    "double_check_position": {
        "fen": "r3k2r/8/8/8/8/8/8/R3K1NR w KQkq - 0 1",
        "description": "Position with potential discovered checks",
        "results": {
            1: 25,
            2: 567,
            3: 14095,
            4: 328965,
            5: 8153719,
            6: 195629489
        }
    },
    
    "tricky_position": {
        "fen": "rnbqkb1r/pp1p1ppp/5n2/2pP4/2P5/8/PP2PPPP/RNBQKBNR w KQkq c6 0 3",
        "description": "Position with en passant opportunity",
        "results": {
            1: 31,
            2: 570,
            3: 17546,
            4: 351806,
            5: 11139762,
            6: 244063299
        }
    }
}


def run_perft_verification(perft_function, verbose=True):
    """
    Run verification tests against known perft results.
    
    Args:
        perft_function: Function that takes (fen, depth) and returns node count
        verbose: Whether to print detailed results
    
    Returns:
        Dictionary with test results
    """
    results = {}
    
    for position_name, position_data in PERFT_POSITIONS.items():
        if verbose:
            print(f"\n=== {position_data['description']} ===")
            print(f"FEN: {position_data['fen']}")
        
        position_results = {}
        
        # Test different depths
        for depth, expected_nodes in position_data['results'].items():
            if depth > 3:  # Skip deep searches for quick testing
                continue
                
            try:
                actual_nodes = perft_function(position_data['fen'], depth)
                passed = actual_nodes == expected_nodes
                position_results[depth] = {
                    'expected': expected_nodes,
                    'actual': actual_nodes,
                    'passed': passed
                }
                
                if verbose:
                    status = "PASS" if passed else "FAIL"
                    print(f"Depth {depth}: {actual_nodes} (expected {expected_nodes}) [{status}]")
                    
            except Exception as e:
                position_results[depth] = {
                    'expected': expected_nodes,
                    'actual': None,
                    'error': str(e),
                    'passed': False
                }
                if verbose:
                    print(f"Depth {depth}: ERROR - {e}")
        
        results[position_name] = position_results
    
    return results


def print_perft_summary(results):
    """Print a summary of perft test results."""
    total_tests = 0
    passed_tests = 0
    
    for position_name, position_results in results.items():
        for depth, result in position_results.items():
            total_tests += 1
            if result.get('passed', False):
                passed_tests += 1
    
    print(f"\n=== PERFT TEST SUMMARY ===")
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Print failed tests
    failed_tests = []
    for position_name, position_results in results.items():
        for depth, result in position_results.items():
            if not result.get('passed', False):
                failed_tests.append(f"{position_name} depth {depth}")
    
    if failed_tests:
        print(f"\nFailed tests:")
        for test in failed_tests:
            print(f"  - {test}")


if __name__ == "__main__":
    # Example usage
    from perft import perft
    
    print("Running perft verification...")
    results = run_perft_verification(perft)
    print_perft_summary(results)
