#!/usr/bin/env python3
"""
UCI Interface for Copycat Chess Engine

This module implements the Universal Chess Interface (UCI) protocol
to make the Copycat Chess Engine compatible with standard chess GUIs.

The UCI protocol allows the engine to communicate with any GUI that supports it,
including Arena, Cutechess, and others.
"""

import sys
import re
import time
import chess
from core.engine import CopycatChessEngine


class CopycatUCI:
    """
    UCI interface for the Copycat Chess Engine.
    Handles communication between the engine and GUI.
    """
    
    def __init__(self):
        """Initialize the UCI interface."""
        self.engine = CopycatChessEngine()
        self.board = chess.Board()
        self.debug_mode = False
        self.name = self.engine.get_name()
        self.author = self.engine.get_author()
        self.options = {
            'Hash': {'type': 'spin', 'default': 16, 'min': 1, 'max': 1024},
            'Style Consistency': {'type': 'spin', 'default': 50, 'min': 0, 'max': 100},
            'Decisiveness': {'type': 'spin', 'default': 50, 'min': 0, 'max': 100},
            'Debug': {'type': 'check', 'default': False}
        }
        
        # For search and timing
        self.search_moves = []
        self.ponder = False
        self.wtime = None
        self.btime = None
        self.winc = None
        self.binc = None
        self.movestogo = None
        self.depth = None
        self.nodes = None
        self.mate = None
        self.movetime = None
        self.infinite = False
        
    def uci(self):
        """Process the UCI command - identification."""
        print(f"id name {self.name}")
        print(f"id author {self.author}")
        
        # Report options
        for name, params in self.options.items():
            if params['type'] == 'spin':
                print(f"option name {name} type {params['type']} default {params['default']} " +
                      f"min {params['min']} max {params['max']}")
            elif params['type'] == 'check':
                print(f"option name {name} type {params['type']} default {str(params['default']).lower()}")
        
        print("uciok")
    
    def debug(self, args):
        """Process the debug command."""
        if len(args) > 0:
            self.debug_mode = (args[0] == "on")
            if self.debug_mode:
                print("info string Debug mode enabled")
            else:
                print("info string Debug mode disabled")
    
    def isready(self):
        """Process the isready command."""
        # Could perform more checks here if needed
        print("readyok")
    
    def setoption(self, args):
        """Process the setoption command."""
        if len(args) < 2 or args[0] != "name":
            return
        
        name = args[1]
        
        # Find the value after "value"
        try:
            value_index = args.index("value")
            value = args[value_index + 1]
        except (ValueError, IndexError):
            return
        
        if name == "Hash":
            try:
                hash_size = int(value)
                # Set hash table size
                if self.debug_mode:
                    print(f"info string Hash size set to {hash_size} MB")
            except ValueError:
                pass
        elif name == "Style Consistency":
            try:
                style_consistency = int(value) / 100.0
                self.engine.style_consistency_weight = style_consistency
                if self.debug_mode:
                    print(f"info string Style Consistency set to {style_consistency}")
            except ValueError:
                pass
        elif name == "Decisiveness":
            try:
                decisiveness = int(value) / 100.0
                self.engine.decisiveness_weight = decisiveness
                if self.debug_mode:
                    print(f"info string Decisiveness set to {decisiveness}")
            except ValueError:
                pass
        elif name == "Debug":
            self.debug_mode = (value.lower() in ["true", "1", "yes", "on"])
            if self.debug_mode:
                print("info string Debug mode enabled")
            else:
                print("info string Debug mode disabled")
    
    def ucinewgame(self):
        """Process the ucinewgame command."""
        self.board = chess.Board()
        # Reset any engine state if needed
    
    def position(self, args):
        """Process the position command."""
        if not args:
            return
        
        # Set up the position
        if args[0] == "startpos":
            self.board = chess.Board()
            args = args[1:]
        elif args[0] == "fen":
            # Extract FEN string
            fen_parts = []
            i = 1
            while i < len(args) and args[i] != "moves":
                fen_parts.append(args[i])
                i += 1
            
            # Create board from FEN
            fen = " ".join(fen_parts)
            try:
                self.board = chess.Board(fen)
                args = args[i:]
            except ValueError:
                print(f"info string Invalid FEN: {fen}")
                return
        
        # Apply moves if any
        if args and args[0] == "moves":
            for move in args[1:]:
                try:
                    self.board.push_uci(move)
                except ValueError:
                    print(f"info string Invalid move: {move}")
                    break
    
    def parse_go_params(self, args):
        """Parse parameters for the go command."""
        # Reset search parameters
        self.search_moves = []
        self.ponder = False
        self.wtime = None
        self.btime = None
        self.winc = None
        self.binc = None
        self.movestogo = None
        self.depth = None
        self.nodes = None
        self.mate = None
        self.movetime = None
        self.infinite = False
        
        # Parse arguments
        i = 0
        while i < len(args):
            if args[i] == "searchmoves":
                i += 1
                while i < len(args) and not args[i].startswith("ponder"):
                    try:
                        move = chess.Move.from_uci(args[i])
                        if move in self.board.legal_moves:
                            self.search_moves.append(move)
                    except ValueError:
                        break
                    i += 1
            elif args[i] == "ponder":
                self.ponder = True
                i += 1
            elif args[i] == "wtime":
                i += 1
                if i < len(args):
                    self.wtime = int(args[i])
                i += 1
            elif args[i] == "btime":
                i += 1
                if i < len(args):
                    self.btime = int(args[i])
                i += 1
            elif args[i] == "winc":
                i += 1
                if i < len(args):
                    self.winc = int(args[i])
                i += 1
            elif args[i] == "binc":
                i += 1
                if i < len(args):
                    self.binc = int(args[i])
                i += 1
            elif args[i] == "movestogo":
                i += 1
                if i < len(args):
                    self.movestogo = int(args[i])
                i += 1
            elif args[i] == "depth":
                i += 1
                if i < len(args):
                    self.depth = int(args[i])
                i += 1
            elif args[i] == "nodes":
                i += 1
                if i < len(args):
                    self.nodes = int(args[i])
                i += 1
            elif args[i] == "mate":
                i += 1
                if i < len(args):
                    self.mate = int(args[i])
                i += 1
            elif args[i] == "movetime":
                i += 1
                if i < len(args):
                    self.movetime = int(args[i])
                i += 1
            elif args[i] == "infinite":
                self.infinite = True
                i += 1
            else:
                i += 1
    
    def calculate_think_time(self):
        """Calculate how much time to think for the current move."""
        # Default think time (milliseconds)
        default_think_time = 1000
        
        # If movetime is specified, use it
        if self.movetime is not None:
            return self.movetime
        
        # Calculate based on clock
        if self.board.turn == chess.WHITE and self.wtime is not None:
            remaining_time = self.wtime
            increment = self.winc or 0
        elif self.board.turn == chess.BLACK and self.btime is not None:
            remaining_time = self.btime
            increment = self.binc or 0
        else:
            return default_think_time
        
        # Safety margin (ms)
        safety_margin = 50
        
        # Estimate moves remaining
        if self.movestogo is not None:
            moves_remaining = self.movestogo
        else:
            # Estimate based on game phase
            phase = self.engine.detect_game_phase(self.board)
            if phase == "opening":
                moves_remaining = 40
            elif phase == "middlegame":
                moves_remaining = 20
            else:  # endgame
                moves_remaining = 10
        
        # Basic time allocation
        base_time = remaining_time / moves_remaining
        
        # Add a portion of the increment
        if increment > 0:
            time_to_use = base_time + (increment * 0.75)
        else:
            time_to_use = base_time * 0.75  # Conservative if no increment
        
        # Apply timing adjustments from the engine
        timing_score = self.engine.calculate_move_timing_score(self.board, remaining_time / 1000.0)
        time_to_use = time_to_use * timing_score
        
        # Apply safety margin
        time_to_use = max(time_to_use - safety_margin, 1)
        
        # Cap at 1/3 of remaining time as a safety measure
        max_time = remaining_time / 3
        time_to_use = min(time_to_use, max_time)
        
        return int(time_to_use)
    
    def go(self, args):
        """Process the go command."""
        # Parse the go parameters
        self.parse_go_params(args)
        
        # Calculate think time (in milliseconds)
        think_time = self.calculate_think_time()
        
        # Convert to seconds for engine
        think_time_seconds = think_time / 1000.0
        
        # Log thinking info if in debug mode
        if self.debug_mode:
            color = "White" if self.board.turn == chess.WHITE else "Black"
            print(f"info string {color} thinking for {think_time_seconds:.2f} seconds")
            print(f"info string Position FEN: {self.board.fen()}")
        
        # Record start time
        start_time = time.time()
        
        # Get the best move from the engine
        remaining_time = None
        if self.board.turn == chess.WHITE and self.wtime is not None:
            remaining_time = self.wtime / 1000.0
        elif self.board.turn == chess.BLACK and self.btime is not None:
            remaining_time = self.btime / 1000.0
            
        best_move = self.engine.select_move(self.board, remaining_time)
        
        # Calculate elapsed time
        elapsed = time.time() - start_time
        
        # If we need to wait to simulate thinking
        if elapsed < think_time_seconds and not self.infinite:
            time.sleep(think_time_seconds - elapsed)
        
        # Send the best move
        if best_move and best_move != chess.Move.null():
            print(f"bestmove {best_move.uci()}")
        else:
            print("bestmove 0000")  # null move as a fallback
    
    def process_command(self, command):
        """Process a UCI command."""
        if not command.strip():
            return True
        
        tokens = command.strip().split()
        if not tokens:
            return True
        
        cmd = tokens[0].lower()
        args = tokens[1:]
        
        if cmd == "uci":
            self.uci()
        elif cmd == "debug":
            self.debug(args)
        elif cmd == "isready":
            self.isready()
        elif cmd == "setoption":
            self.setoption(args)
        elif cmd == "ucinewgame":
            self.ucinewgame()
        elif cmd == "position":
            self.position(args)
        elif cmd == "go":
            self.go(args)
        elif cmd == "stop":
            # Handle stop command
            pass
        elif cmd == "ponderhit":
            # Handle ponderhit command
            pass
        elif cmd == "quit":
            return False
        else:
            if self.debug_mode:
                print(f"info string Unknown command: {cmd}")
        
        return True
    
    def main_loop(self):
        """Main UCI protocol loop."""
        while True:
            try:
                command = input()
                if not self.process_command(command):
                    break
            except EOFError:
                break
            except Exception as e:
                print(f"info string Error: {str(e)}")
