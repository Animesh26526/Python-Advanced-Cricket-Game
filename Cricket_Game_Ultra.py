import random
from time import sleep as s

class Player:
    def __init__(self, name):
        self.name = name
        self.runs = 0
        self.balls = 0
        self.fours = 0
        self.sixes = 0
        self.strikerate = 0
        self.dismissed = False
        self.wicket_taking_bowler_name = ""
        self.how_out = ""
        self.wickets = 0
        self.balls_bowled = 0
        self.runs_conceded = 0

    def add_runs(self, runs):
        self.runs += runs
        self.balls += 1
        self.strikerate = float('%.2f' % ((self.runs / self.balls) * 100)) if self.balls > 0 else 0

    def __str__(self):
        status = f"{self.runs}({self.balls})"
        if not self.dismissed:
            status += f"* S/R: {self.strikerate}"
        else:
            status += f" S/R: {self.strikerate}"
        return f"{self.name} - {status}"

class Team:
    def __init__(self, name, captain):
        self.name = name
        self.captain = captain
        self.players = []
        self.fast_bowlers = []
        self.spin_bowlers = []
        self.score = 0
        self.runrate = 0
        self.reviews_left = 2
        self.session = 1
        self.day = 1
        self.super_over = False
        self.super_over_players = []
        self.current_bowler = None
        self.current_bowler_name = None

    def add_player(self, player):
        self.players.append(player)

    def add_fast_bowler(self, name):
        self.fast_bowlers.append(name)

    def add_spin_bowler(self, name):
        self.spin_bowlers.append(name)
    
    def make_current_bowler(self, name):
        return Player(name)

    def get_next_batsman(self):
        for player in (self.players if not self.super_over else self.super_over_players):
            if not player.dismissed and player.balls == 0:
                return player
        return None
    
    def short_form_score(self, how_out):
        self.how_out = how_out
        if self.how_out == "Caught and Bowled":
            return "c & b"
        elif self.how_out == "L.B.W":
            return "lbw"
        elif self.how_out == "Caught" or self.how_out == "Edged And Caught Behind":
            return "c"
        elif self.how_out == "Stumped":
            return "st"
        else:
            return self.how_out


    def print_scorecard(self):
        print(f"\n--- {self.name} Scorecard ---\n")
        for p in [player for player in self.players if player.balls > 0 or player.dismissed]:
            status = f" - {p.runs}({p.balls})"
            if p.dismissed:    
                if p.how_out == "Bowled":
                    status += f" 4s: {p.fours} 6s: {p.sixes} S/R: {p.strikerate} b {p.wicket_taking_bowler_name}"
                else:
                    status += f" 4s: {p.fours} 6s: {p.sixes} S/R: {p.strikerate} ({self.short_form_score(p.how_out)}) b {p.wicket_taking_bowler_name}"
            elif p.balls > 0:
                status += f"*  4s: {p.fours} 6s: {p.sixes} S/R: {p.strikerate}"
            print(f"{p.name}{status}")

    def print_bowler_scorecard(self):
        print("\nBowler Scorecard:")
        for bowler in self.players:
            if bowler.balls_bowled > 0:
                overs = bowler.balls_bowled // 6 + (bowler.balls_bowled % 6) / 10
                economy = round(bowler.runs_conceded / (bowler.balls_bowled / 6), 2) if bowler.balls_bowled >= 6 else bowler.runs_conceded
                print(f"{bowler.name}: Overs: {overs}, Runs: {bowler.runs_conceded}, Wickets: {bowler.wickets}, Economy: {economy}")


class Match:
    def __init__(self, overs, home_team, away_team):
        self.match_format = "T20"
        self.powerplay = True
        self.session_changed = 1
        self.day_changed = 1
        self.overs = overs
        self.total_balls = self.overs * 6
        self.balls_per_over = 6
        self.home_team = home_team
        self.away_team = away_team
        self.innings = 1
        self.batting_team = None
        self.bowling_team = None
        self.striker = None
        self.non_striker = None
        self.balls_bowled = 0
        self.overs_bowled = 0
        self.used_bowlers = []
        self.target = None
        self.super_over = False
        self.Available_Shots = []
        self.spin_deliveries = ["Leg Spin", "Off Spin", "Top Spin", "Arm Ball", "Flipper"]
        self.fast_deliveries = ["Straight", "In Swing", "Out Swing", "Leg Cutter", "Off Cutter", "Bouncer"]
        self.shots = ["Straight Drive", "Off Drive", "Cover Drive", "On Drive", "Pull", "Scoop Shot", "Cut", "Square Cut", "Defensive Shot", "Leave"]
        self.result_types = [
            ("No Run", "1 Run", "2 Runs", "3 Runs", "4 Runs", "6 Runs"),
            ("Wide", "Leg Bye", "No Ball", "Wide Four"),
            ("L.B.W", "Bowled", "Caught", "Caught and Bowled", "Run Out", "Stumped", "Edged And Caught Behind")
        ]

    def toss(self):
        print(f"\nCaptains: {self.home_team.captain} and {self.away_team.captain}")
        s(1)
        call = input(f"{self.home_team.name}, call the toss (Heads/Tails): ").title()
        if call not in ["Heads", "Tails"]:
            print("Invalid input. Please enter 'Heads' or 'Tails'.")
            return self.toss()
        print("Tossing the coin...")
        s(2)
        result = random.choice(["Heads", "Tails"])
        print(f"Coin shows: {result}")
        s(1)
        if call == result:
            choice = input(f"{self.home_team.name} won the toss! Choose Bat or Bowl: ").title()
            if choice == "Bat":
                self.batting_team, self.bowling_team = self.home_team, self.away_team
            else:
                self.batting_team, self.bowling_team = self.away_team, self.home_team
        else:
            choice = input(f"{self.away_team.name} won the toss! Choose Bat or Bowl: ").title()
            if choice == "Bat":
                self.batting_team, self.bowling_team = self.away_team, self.home_team
            else:
                self.batting_team, self.bowling_team = self.home_team, self.away_team

    def start_innings(self):
        self.striker = self.batting_team.players[0]
        self.non_striker = self.batting_team.players[1]
        self.balls_bowled = 0
        self.overs_bowled = 0
        self.batting_team.score = 0
        self.batting_team.wickets = 0
        self.batting_team.runs_conceded = 0
        self.batting_team.reviews_left = 2
        self.bowling_team.runs_conceded = 0
        self.bowling_team.wickets = 0
        self.bowling_team.reviews_left = 2
        for player in self.batting_team.players:
            player.runs = 0
            player.balls = 0
            player.fours = 0
            player.sixes = 0
            player.dismissed = False
            player.wicket_taking_bowler_name = ""
            player.how_out = ""
        for player in self.bowling_team.players:
            player.runs = 0
            player.balls = 0
            player.fours = 0
            player.sixes = 0
            player.dismissed = False
            player.wicket_taking_bowler_name = ""
            player.how_out = ""
        self.bowling_team.current_bowler = None
        self.bowling_team.current_bowler_name = None
        self.used_bowlers = []

    def select_bowler(self):
        bowlers = self.bowling_team.fast_bowlers + self.bowling_team.spin_bowlers
        options = [b for b in bowlers if b != self.bowling_team.current_bowler_name]
        for i, bowler in enumerate(bowlers):
            print(f"{i+1}. {bowler}")
        try:
            bowler_choice = int(input(f"Choose the Bowler (1-{i+1}): ")) - 1
        except ValueError:
            print("Invalid input: Please enter a valid number.")
            return self.select_bowler()
        if bowler_choice < 0 or bowler_choice >= len(bowlers):
            print("Invalid choice. Please try again.")
            return self.select_bowler()
        self.bowling_team.current_bowler_name = bowlers[bowler_choice]
        self.bowling_team.current_bowler = self.bowling_team.make_current_bowler(self.bowling_team.current_bowler_name)
        print(f"\n{self.bowling_team.current_bowler_name} will bowl this over.")
        s(1)

    def swap_strike(self):
        self.striker, self.non_striker = self.non_striker, self.striker

    def parse_runs(self, result):
        for part in result.split():
            if part.isdigit(): return int(part)
        return 0

    def drs_review(self, dismissal_type):
        print("\nTV Umpire to Director... Player Review for:", dismissal_type.upper())
        s(1)
        print("Umpire's Decision: OUT... Checking Replay...")
        s(1)

        successful_review = False
        reviewed_by = "batting" if dismissal_type != "Leg Bye" else "bowling"

        if dismissal_type == "L.B.W":
            edge = random.choices(["No Bat", "Bat"], [0.95, 0.05])[0]
            pitching = random.choices(["In Line", "Outside Off", "Outside Leg"], [0.6, 0.25, 0.15])[0]
            impact = random.choices(["In Line", "Umpire's Call", "Outside"], [0.7, 0.2, 0.1])[0]
            wickets = random.choices(["Hitting", "Umpire's Call", "Missing"], [0.6, 0.25, 0.15])[0]
            print(f"UltraEdge: {edge}\nPitching: {pitching}\nImpact: {impact}\nWickets: {wickets}")
            s(2)
            if edge == "Bat" or pitching == "Outside Leg" or impact == "Outside" or wickets == "Missing":
                print("Decision Overturned! Not Out.")
                successful_review = True
                result = "Not Out"
            elif (pitching == "Outside Off" and impact == "Outside" and self.shot == "Leave" and edge == "No Bat" and wickets == "Hitting"):
                print("No shot offered, everything aligned. Decision Stands. Out!")
                result = "L.B.W"
            else:
                print("Umpire's Call Stands. Batter is Out.")
                result = "L.B.W"

        elif dismissal_type == "Leg Bye":
            edge = random.choices(["No Bat", "Bat"], [0.98, 0.02])[0]
            pitching = random.choices(["In Line", "Outside Off", "Outside Leg"], [0.3, 0.4, 0.3])[0]
            impact = random.choices(["In Line", "Umpire's Call", "Outside"], [0.3, 0.4, 0.3])[0]
            wickets = random.choices(["Hitting", "Umpire's Call", "Missing"], [0.3, 0.2, 0.5])[0]
            print(f"UltraEdge: {edge}\nPitching: {pitching}\nImpact: {impact}\nWickets: {wickets}")
            s(2)
            if edge == "No Bat" and ((pitching == "In Line" and impact == "In Line" and wickets == "Hitting") or (pitching == "Outside Off" and impact == "Outside" and self.shot == "Leave" and wickets == "Hitting")):
                print("Review Successful. Changed to L.B.W.")
                successful_review = True
                result = "L.B.W"
            else:
                print("Review Unsuccessful. Stays Leg Bye.")
                result = "Leg Bye"

        elif dismissal_type == "Run Out":
            decision = random.choices(["Out", "Not Out"], [0.8, 0.2])[0]
            print(f"Third Umpire View: {decision}")
            s(1)
            if decision == "Not Out":
                print("Review Successful. Overturned to Not Out.")
                successful_review = True
                result = "Not Out"
            else:
                print("Review Unsuccessful. Run Out stands.")
                result = "Run Out"

        elif dismissal_type == "Edged And Caught Behind":
            edge = random.choices(["No Edge", "Edge"], [0.2, 0.8])[0]
            print(f"UltraEdge shows: {edge}")
            s(1)
            if edge == "No Edge":
                print("Review Successful. No contact. Not Out.")
                successful_review = True
                result = "Not Out"
            else:
                print("Review Unsuccessful. Out stands.")
                result = "Edged And Caught Behind"

        elif dismissal_type == "Stumped":
            foot_status = random.choices(["Foot In", "Foot Out"], [0.2, 0.8])[0]
            print(f"Replay shows: {foot_status}")
            s(1)
            if foot_status == "Foot In":
                print("Review Successful. Batter was inside. Not Out.")
                successful_review = True
                result = "Not Out"
            else:
                print("Review Unsuccessful. Stumped remains.")
                result = "Stumped"

        else:
            print("Review system not applicable to this type.")
            result = dismissal_type

        if not successful_review:
            if reviewed_by == "batting":
                self.batting_team.reviews_left -= 1
                print(f"Batting team reviews left: {self.batting_team.reviews_left}")
            else:
                self.bowling_team.reviews_left -= 1
                print(f"Bowling team reviews left: {self.bowling_team.reviews_left}")

        return result
    
    def handle_dismissal_with_drs(self, result):
        if result in ["L.B.W", "Run Out", "Edged And Caught Behind", "Stumped"] and self.batting_team.reviews_left > 0:
            review = input("Do you want to take a review? (yes/no): ").lower()
            if review == "yes":
                result = self.drs_review(result)

        elif result == "Leg Bye" and self.bowling_team.reviews_left > 0:
            review = input("Bowling team wants to review for LBW? (yes/no): ").lower()
            if review == "yes":
                result = self.drs_review("Leg Bye")

        return result

        
    def normalize_weights(self, outcome_list):
        total = sum(weight for _, weight in outcome_list)
        if total == 0:
            return outcome_list
        return [(label, round((weight / total) * 100, 2)) for label, weight in outcome_list]


    def Shot_selection(self):
        if self.delivery == "Leg Spin":
            if self.stumps == "Touching":
                self.Available_Shots = ["Straight Drive", "Off Drive", "Cover Drive", "Defensive Shot"]
            else:
                self.Available_Shots = ["Straight Drive", "Off Drive", "Cover Drive", "Defensive Shot", "Leave"]
        elif self.delivery == "Off Spin":
            if self.stumps == "Touching":
                self.Available_Shots = ["Straight Drive", "On Drive", "Pull", "Scoop Shot", "Defensive Shot"]
            else:
                self.Available_Shots = ["Straight Drive", "On Drive", "Pull", "Defensive Shot", "Leave"]
        elif self.delivery == "Top Spin":
            if self.stumps == "Touching":
                self.Available_Shots = ["On Drive", "Pull", "Hook", "Defensive Shot"]
            else:
                self.Available_Shots = ["Cut", "Square Cut", "Defensive Shot", "Leave"]
        elif self.delivery == "Arm Ball":
            if self.stumps == "Touching":
                self.Available_Shots = ["On Drive", "Sweep", "Leg Glance", "Defensive Shot"]
            else:
                self.Available_Shots = ["Off Drive", "Square Cut", "Cut", "Defensive Shot", "Leave"]
        elif self.delivery == "Flipper":
            if self.stumps == "Touching":
                self.Available_Shots = ["Straight Drive", "On Drive", "Leg Glance", "Defensive Shot"]
            else:
                self.Available_Shots = ["Straight Drive", "Off Drive", "Cover Drive", "Defensive Shot", "Leave"]
        elif self.delivery == "Straight":
            if self.stumps == "Touching":
                self.Available_Shots = ["Straight Drive", "On Drive"]
            else:
                self.Available_Shots = ["Straight Drive", "Off Drive", "Cover Drive", "Defensive Shot", "Leave"]
        elif self.delivery == "In Swing":
            if self.stumps == "Touching":
                self.Available_Shots = ["Straight Drive", "On Drive", "Scoop Shot", "Defensive Shot"]
            else:
                self.Available_Shots = ["Straight Drive", "Off Drive", "Cover Drive", "Defensive Shot", "Leave"]
        elif self.delivery == "Out Swing":
            if self.stumps == "Touching":
                self.Available_Shots = ["Straight Drive", "Off Drive", "Defensive Shot"]
            else:
                self.Available_Shots = ["Straight Drive", "Off Drive", "Cover Drive", "Defensive Shot", "Leave"]
        elif self.delivery == "Leg Cutter":
            if self.stumps == "Touching":
                self.Available_Shots = ["Straight Drive", "Off Drive", "Leg Glance", "Defensive Shot"]
            else:
                self.Available_Shots = ["Cut", "Square Cut", "Leave"]
        elif self.delivery == "Off Cutter":
            if self.stumps == "Touching":
                self.Available_Shots = ["Straight Drive", "On Drive", "Pull", "Leg Glance", "Defensive Shot"]
            else:
                self.Available_Shots = ["Straight Drive", "Off Drive", "Cover Drive", "Defensive Shot", "Leave"]
        elif self.delivery == "Bouncer":
            if self.stumps == "Touching":
                self.Available_Shots = ["On Drive", "Pull"]
            else:
                self.Available_Shots = ["Hook", "Leave"]

        print(f"\nAvailable Shots:")
        for i, shot in enumerate(self.Available_Shots):
            print(f"{i+1}. {shot}")
        try:
            shot_choice = int(input(f"Choose your shot (1-{i+1}): ")) - 1
        except ValueError:
            print("Invalid input: Please enter a valid number.")
            return self.Shot_selection()
        if shot_choice < 0 or shot_choice >= len(self.Available_Shots):
            print("Invalid choice. Please try again.")
            return self.Shot_selection()
        self.shot = self.Available_Shots[shot_choice]

    def normalize_weights(self, outcome_list):
        total = sum(weight for _, weight in outcome_list)
        return [(label, round((weight / total) * 100, 2)) for label, weight in outcome_list] if total > 0 else outcome_list

    # --- Base run probabilities per format and phase ---
    def base_runs(self, match_format, powerplay):
        # Returns list of tuples (label, weight)
        if self.match_format == "T20":
            if powerplay:
                return [("No Run", 15), ("1 Run", 30), ("2 Runs", 10), ("3 Runs", 5), ("4 Runs", 25), ("6 Runs", 15)]
            else:
                return [("No Run", 25), ("1 Run", 25), ("2 Runs", 10), ("3 Runs", 5), ("4 Runs", 20), ("6 Runs", 15)]
        elif self.match_format == "ODI":
            if powerplay:
                return [("No Run", 20), ("1 Run", 30), ("2 Runs", 15), ("3 Runs", 5), ("4 Runs", 20), ("6 Runs", 10)]
            else:
                return [("No Run", 30), ("1 Run", 30), ("2 Runs", 10), ("3 Runs", 5), ("4 Runs", 15), ("6 Runs", 5)]
        elif self.match_format == "Test":
            if powerplay:
                return [("No Run", 30), ("1 Run", 20), ("2 Runs", 20), ("3 Runs", 3), ("4 Runs", 5), ("6 Runs", 3)]
        else:
            # Default to T20 normal
            return [("No Run", 25), ("1 Run", 25), ("2 Runs", 10), ("3 Runs", 5), ("4 Runs", 20), ("6 Runs", 15)]

    # --- Dismissals per shot/delivery/stumps, adjusted for format and powerplay ---
    # Note: The dismissal weights below are base values and can be scaled per format if desired.
    # For simplicity, I keep them same here but you can add format param and adjust weights as needed.

    def dismissals_leave(self, stumps, match_format, powerplay):
        if stumps == "Touching":
            base = [("Bowled", 60), ("L.B.W", 20), ("Edged And Caught Behind", 5)]
            return self.scale_dismissal_weights(base, match_format, powerplay)
        else:
            return []

    def dismissals_defensive(self, match_format, powerplay):
        base = [("Caught", 10), ("L.B.W", 5)]
        return self.scale_dismissal_weights(base, match_format, powerplay)

    def dismissals_scoop_bouncer(self, match_format, powerplay):
        base = [("Caught", 35), ("Stumped", 5), ("Edged And Caught Behind", 10), ("Run Out", 10)]
        return self.scale_dismissal_weights(base, match_format, powerplay)

    def dismissals_pull_bouncer(self, match_format, powerplay):
        base = [("Caught", 20), ("Edged And Caught Behind", 5), ("Run Out", 10)]
        return self.scale_dismissal_weights(base, match_format, powerplay)

    def dismissals_cut_top_flipper(self, match_format, powerplay):
        base = [("Caught", 20), ("Edged And Caught Behind", 10), ("Run Out", 10)]
        return self.scale_dismissal_weights(base, match_format, powerplay)

    def dismissals_sweep_top_leg(self, match_format, powerplay):
        base = [("Stumped", 15), ("Caught", 10), ("Run Out", 10), ("Edged And Caught Behind", 5)]
        return self.scale_dismissal_weights(base, match_format, powerplay)

    def dismissals_straight_arm_leg(self, match_format, powerplay):
        base = [("L.B.W", 5), ("Caught", 5), ("Run Out", 10)]
        return self.scale_dismissal_weights(base, match_format, powerplay)

    def dismissals_off_cover_drive(self, match_format, powerplay):
        base = [("Caught", 10), ("Run Out", 10), ("Edged And Caught Behind", 5)]
        return self.scale_dismissal_weights(base, match_format, powerplay)

    def dismissals_default(self, match_format, powerplay):
        base = [
            ("Caught", 15), ("L.B.W", 10), ("Run Out", 5),
            ("Edged And Caught Behind", 5), ("Stumped", 5), ("Caught and Bowled", 5)
        ]
        return self.scale_dismissal_weights(base, match_format, powerplay)

    def scale_dismissal_weights(self, dismissals, match_format, powerplay):
        # Example scaling: Test cricket is more defensive, so reduce dismissal probabilities a bit
        scale = 1.0
        if self.match_format == "Test":
            scale = 0.7
        elif self.match_format == "ODI":
            scale = 0.85
        elif self.match_format == "T20":
            scale = 1.0
        # Could also vary by powerplay if needed
        scaled = [(label, max(1, int(weight * scale))) for label, weight in dismissals]
        return scaled

    def get_dismissals(self, shot, delivery, stumps, match_format, powerplay):
        if shot == "Leave":
            return self.dismissals_leave(stumps, match_format, powerplay)
        elif "Defensive" in shot:
            return self.dismissals_defensive(match_format, powerplay)
        elif shot == "Scoop Shot" and delivery == "Bouncer":
            return self.dismissals_scoop_bouncer(match_format, powerplay)
        elif shot == "Pull" and delivery == "Bouncer":
            return self.dismissals_pull_bouncer(match_format, powerplay)
        elif shot in ["Cut", "Square Cut"] and delivery in ["Off Cutter", "Top Spin", "Flipper"]:
            return self.dismissals_cut_top_flipper(match_format, powerplay)
        elif shot == "Sweep Shot" and delivery in ["Top Spin", "Leg Spin"]:
            return self.dismissals_sweep_top_leg(match_format, powerplay)
        elif shot in ["Straight Drive", "On Drive"] and delivery in ["Straight", "Arm Ball", "Leg Cutter"]:
            return self.dismissals_straight_arm_leg(match_format, powerplay)
        elif shot in ["Off Drive", "Cover Drive"] and delivery in ["In Swing", "Out Swing", "Off Cutter"]:
            return self.dismissals_off_cover_drive(match_format, powerplay)
        else:
            return self.dismissals_default(match_format, powerplay)

    def Probability_matrix(self, match_format="T20", powerplay=False):
        outcomes = {}
        for shot in self.shots:
            for delivery in self.deliveries:
                for stumps in ["Touching", "Not Touching"]:
                    base_runs = self.base_runs(match_format, powerplay)
                    dismissals = self.get_dismissals(shot, delivery, stumps, match_format, powerplay)
                    total_outcomes = base_runs + dismissals
                    outcomes[(shot, delivery, stumps)] = self.normalize_weights(total_outcomes)
        return outcomes

    def delivery_extras(self):
        return self.normalize_weights([
            ("No Ball", 5), ("Wide", 5), ("Leg Bye", 3), ("Run Out", 5), ("None", 80),
            ("Wide Four", 2)
        ])

    def generate_ball_result(self, match_format="T20", powerplay=False):
        self.Shot_selection()
        extras = self.delivery_extras()
        labels, weights = zip(*extras)
        extra_outcome = random.choices(labels, weights=weights)[0]
        if extra_outcome != "None":
            return extra_outcome

        key = (self.shot, self.delivery, self.stumps)
        matrix = self.Probability_matrix(match_format, powerplay)
        outcomes = matrix.get(key, [("No Run", 60), ("1 Run", 20), ("Caught", 10), ("Run Out", 10)])
        labels, weights = zip(*outcomes)
        return random.choices(labels, weights=weights)[0]

    def print_over_summary(self):
        print("\nOver Summary:")
        print(f"{self.bowling_team.current_bowler_name}: {', '.join(self.over_log)}")

    def short_form(self,result):
        if result == "No Run":
            return "0"
        elif result == "1 Run":
            return "1"
        elif result == "2 Runs":
            return "2"
        elif result == "3 Runs":
            return "3"
        elif result == "4 Runs":
            return "4"
        elif result == "6 Runs":
            return "6"
        elif result == "Wide":
            return "WD"
        elif result == "Wide Four":
            return "5WD"
        elif result == "Leg Bye":
            return "LB"
        elif result == "No Ball":
            return "NB"
        elif result in self.result_types[2]:
            return "W" 

    def bowl_ball(self,wickets_disabled=False):
        self.wickets_disabled = False
        self.catch_Drop = False
        self.deliveries = self.fast_deliveries if self.bowling_team.current_bowler_name in self.bowling_team.fast_bowlers else self.spin_deliveries
        print("\n")
        for i,delivery in enumerate(self.deliveries):
            print(f"{i+1}. {delivery}")
        
        try:
            delivery_choice = int(input("Choose your Bowl (1-6): ")) - 1
        except ValueError:
            print("Invalid input: Please enter a valid number.")
            return self.bowl_ball(wickets_disabled=False)
        if delivery_choice < 0 or delivery_choice > len(self.deliveries):   
            print("Invalid choice. Please try again.")
            return self.bowl_ball(wickets_disabled=False)
        self.delivery = self.deliveries[delivery_choice]
        self.stumps = random.choice(["Touching", "Not Touching"])
        self.result = self.generate_ball_result(self.match_format, self.powerplay)
        
        while (self.result == "Wide" or self.result == "Wide Four") and self.stumps == "Touching":
            self.result = self.generate_ball_result(self.match_format, self.powerplay)
        if self.result == "L.B.W" and self.stumps == "Not Touching":
            self.result = "Leg Bye"
        if self.shot == "Leave":
            self.result = "No Run"
        if self.result == "Caught":
            self.result = random.choices(["No Run", "1 Run", "2 Runs", "3 Runs", "4 Runs", "6 Runs", "Caught"], weights=[2, 3, 4, 1, 3, 2, 85])[0]
            self.catch_Drop = True if not self.result == "Caught" else False
        if self.result == "Caught and Bowled":
            self.result = random.choices(["No Run", "1 Run", "2 Runs", "3 Runs", "4 Runs", "6 Runs", "Caught and Bowled"], weights=[4, 3, 4, 1, 3, 0, 85])[0]
            self.catch_Drop = True if not self.result == "Caught and Bowled" else False
        if self.result == "Edged And Caught Behind":
            self.result = random.choices(["No Run", "1 Run", "2 Runs", "3 Runs", "4 Runs", "6 Runs", "Edged And Caught Behind"], weights=[3, 4, 4, 1, 3, 0, 85])[0]
            self.catch_Drop = True if not self.result == "Edged And Caught Behind" else False
        if self.result in ["L.B.W", "Bowled", "Caught", "Caught and Bowled", "Stumped", "Edged And Caught Behind"] and wickets_disabled:
            self.result = random.choices(["No Run", "1 Run", "2 Runs", "3 Runs", "4 Runs", "6 Runs", "Run Out"], weights=[30, 40, 20, 2, 6, 1, 1])[0]
        while self.result == "Bowled" and self.stumps == "Not Touching":
            self.result = self.generate_ball_result(self.match_format, self.powerplay)

        self.result = self.handle_dismissal_with_drs(self.result)

        print(f"\n{self.bowling_team.current_bowler_name} to {self.striker.name}: {self.delivery}")
        s(1)
        print(f"Stumps: {self.stumps}")
        s(1)
        if self.catch_Drop:
            print("Catch Dropped!")
            s(1)
        print(f"Result: {self.result}", end=" " if self.result == "No Ball" else "\n")
        s(1)

        if self.result == "Wide":
            self.batting_team.score += 1
            self.bowling_team.current_bowler.runs_conceded += 1
            self.over_log.append(self.short_form(self.result))
            return
        elif self.result == "No Ball":  
            self.batting_team.score += 1
            self.bowling_team.current_bowler.runs_conceded += 1
            while self.result == "Wide" or self.result == "Wide Four" or self.result == "No Ball" or self.result in ["L.B.W", "Bowled", "Caught", "Caught and Bowled", "Stumped", "Edged And Caught Behind"]:
                self.result = self.generate_ball_result(self.match_format, self.powerplay)
            s(1)
            print(f"+ {self.result}")
            self.over_log.append(f"NB + {self.short_form(self.result) if self.result != 'No Run' else 'NB'}")
            s(1)
            if self.result == "Leg Bye":
                self.batting_team.score += 1
            elif self.result == "Run Out": 
                self.striker.dismissed = True
                self.striker.how_out = "Run Out"
                self.striker.wicket_taking_bowler_name = self.bowling_team.current_bowler_name
                print(f"OUT! {self.striker.name} - Run Out")
                self.batting_team.wickets += 1
                next_bat = self.batting_team.get_next_batsman()
                if next_bat: self.striker = next_bat
            else:
                runs = self.parse_runs(self.result)
                self.striker.add_runs(runs)
                if runs == 4:
                    self.striker.fours += 1
                elif runs == 6:
                    self.striker.sixes += 1
                self.batting_team.score += runs
                self.bowling_team.current_bowler.runs_conceded += runs
                if runs % 2 == 1: self.swap_strike()
            while self.result in self.result_types[1] and self.match_format != "Test":
                print("Free Hit!")
                self.bowl_ball(wickets_disabled=True)
            return
        elif self.result == "Wide Four":
            self.batting_team.score += 5
            self.bowling_team.current_bowler.runs_conceded += 5
            self.over_log.append(self.short_form(self.result))
            return
        elif self.result == "Leg Bye":
            self.batting_team.score += 1
            self.balls_bowled += 1
            self.bowling_team.current_bowler.balls_bowled += 1
            self.over_log.append(self.short_form(self.result))
            return

        if self.result in self.result_types[2]:
            self.striker.balls += 1
            self.striker.dismissed = True
            self.striker.how_out = self.result
            self.striker.wicket_taking_bowler_name = self.bowling_team.current_bowler_name
            self.bowling_team.current_bowler.wickets += 1
            self.over_log.append(self.short_form(self.result))
            print(f"OUT! {self.striker.name} - {self.result}")
            self.batting_team.wickets += 1
            next_bat = self.batting_team.get_next_batsman()
            if next_bat: self.striker = next_bat
        else:
            runs = self.parse_runs(self.result)
            self.striker.add_runs(runs)
            if runs == 4:
                self.striker.fours += 1
            elif runs == 6:
                self.striker.sixes += 1
            self.batting_team.score += runs
            self.bowling_team.current_bowler.runs_conceded += runs
            self.over_log.append(self.short_form(self.result))
            if runs % 2 == 1: self.swap_strike()

        self.balls_bowled += 1
        self.bowling_team.current_bowler.balls_bowled += 1
       

    def display_score(self):
        print(f"\n{self.batting_team.name} - {self.batting_team.score}/{self.batting_team.wickets}")
        print(self.striker)
        print(self.non_striker)
        self.batting_team.runrate = float('%.2f' % ((self.batting_team.score / (self.balls_bowled / 6)))) if self.balls_bowled > 0 else 0
        print(f"Runrate: {self.batting_team.runrate}")
        if self.innings == 2:
            if self.batting_team.score < self.target:
                print(f"To Win: {self.target - self.batting_team.score} Runs from {self.total_balls - self.balls_bowled} Balls")

    def play_innings(self):
        self.start_innings()
        self.display_score()
        if self.innings == 1 and self.match_format == "Test":
            self.overs_completed = 0
        elif self.innings == 2 and self.match_format == "Test":
            self.overs_completed = self.upto_first_innings_overs_bowled
        elif self.innings == 3 and self.match_format == "Test":
            self.overs_completed = self.upto_second_innings_overs_bowled
        elif self.innings == 4 and self.match_format == "Test":
            self.overs_completed = self.upto_third_innings_overs_bowled

        while (self.balls_bowled < self.total_balls and self.match_format != "Test") or (self.batting_team.wickets < 10 and self.match_format == "Test" and self.check_test_match_draw(self.overs_bowled + self.overs_completed, 5*self.overs)):
            self.select_bowler()
            self.over_log = []
            if self.balls_bowled > 0:
            	self.overs_bowled +=1
            while self.balls_bowled < self.balls_per_over*(self.overs_bowled + 1):
                self.bowl_ball(wickets_disabled=False)
                self.display_score()
                if self.balls_bowled % 6 == 0 and self.result not in self.result_types[1]:
                    print("--- End of Over ---\n")
                    self.print_over_summary()
                    print("\n")
                    self.swap_strike()
                    if self.match_format == "T20" and self.overs_bowled >= (6/20)*self.overs and self.powerplay:
                        self.powerplay = False
                        print("Powerplay Over!")
                    elif self.match_format == "ODI" and self.overs_bowled >= (10/50)*self.overs and self.powerplay: 
                        self.powerplay = False
                        print("Powerplay Over!")
                    elif self.match_format == "Test" and self.overs_bowled >= self.batting_team.session*(30/90)*self.overs and self.session_changed == self.batting_team.session:
                        self.session_changed += 1
                        self.batting_team.session += 1
                        print(f"Session {self.batting_team.session - 1} Over!")
                        if self.overs_bowled >= self.overs and self.batting_team.session == 3*self.batting_team.day and self.day_changed == self.batting_team.day:
                            self.batting_team.day += 1
                            self.day_changed += 1
                            print(f"Day {self.batting_team.day - 1} Over!")
                            print(f"New Day: {self.batting_team.day}")
                        print(f"New Session: {self.batting_team.session}")
                    
                    if self.match_format == "Test":
                        input("Press Enter to continue... or Press 'd' to declare innings: ")
                        if input().lower() == 'd':
                            print(f"{self.batting_team.name} has declared the innings.")
                            return
                    else:
                        input("Press Enter to continue...")
                    s(1)
                if self.batting_team.wickets == 2 and self.super_over == True:
                    print("Innings Over!")
                    return
                if self.batting_team.wickets == 10:
                    print("All Out!")
                    return
                if self.innings == 2 and self.batting_team.score >= self.target and self.match_format != "Test":
                    print("Target chased down!")
                    return
                if self.innings == 4 and self.batting_team.score >= self.target and self.match_format == "Test":
                    print("Target chased down!")
                    return

    def man_of_the_match(self):
        all_players = self.home_team.players + self.away_team.players
        self.top_score = float('-inf')
        self.top_player = None

        for player in all_players:
            runs = player.runs
            balls = player.balls if hasattr(player, 'balls') else 0
            wickets = player.wickets
            if player.balls_bowled >= 6:
                economy = round(player.runs_conceded / (player.balls_bowled / 6), 2)
            else:
                economy = player.runs_conceded

            batting_impact = runs - (balls / 2)
            bowling_impact = (wickets * 25) - (economy * 2)
            impact = batting_impact + bowling_impact

            if impact > self.top_score:
                self.top_score = impact
                self.top_player = player

        if not self.super_over:
            if self.top_player:
                print(f"\n\U0001F3C6 Man of the Match: {self.top_player.name}")
                print(f"Batting: {self.top_player.runs} runs in {self.top_player.balls} balls")
                print(f"Bowling: {self.top_player.wickets} wickets, {self.top_player.runs_conceded} runs in {self.top_player.balls_bowled // 6}.{self.top_player.balls_bowled % 6} overs")
            else:
                print("No standout performance for Man of the Match.")

    def play_super_over(self):
        self.super_over = True
        print("\n--- Scores are level. Super Over Begins! ---")
        s(1)
        input("Press Enter to Start First Super Over Innings...")
        s(1)

        print(f"\n{self.batting_team.name} batting first in Super Over.")
        print(f"\nEnter 4 players for {self.batting_team} to Play in Super Over:")
        for i in range(4):
            self.batting_team.super_over_players.append(Player(input(f"Player {i+1}: ")))
        #Bowler will be selected by self bowling team itself, no change
        self.start_innings()
        self.play_innings()
        team1_super_score = self.batting_team.score

        # Second Super Over: Team2 chases
        print(f"\n{self.bowling_team.name} chasing in Super Over. Target: {team1_super_score + 1}")
        s(1)
        input("Press Enter to start second Super Over innings...")
        s(1)
        self.batting_team, self.bowling_team = self.bowling_team, self.batting_team
        print(f"\nEnter 4 players for {self.batting_team} to Play in Super Over:")
        for i in range(4):
            self.batting_team.super_over_players.append(Player(input(f"Player {i+1}: ")))
        s(1)
        self.start_innings()
        self.target = team1_super_score + 1
        self.play_innings()
        team2_super_score = self.batting_team.score

        # Result
        if team2_super_score > team1_super_score:
            print(f"\n{self.batting_team.name} wins the Match by {team2_super_score - team1_super_score} runs in Super Over!")
        elif team2_super_score < team1_super_score:
            print(f"\n{self.bowling_team.name} wins the Match by {2 - self.batting_team.wickets} wickets in Super Over!")
        else:
            print("\nSuper Over is also tied! Another Super Over to Follow!")
            return self.play_super_over()


    def play_match(self, match_format="T20"):
        self.match_format = match_format
        if self.match_format == "Test":
            self.play_test_match()
            return
        self.toss()
        self.innings = 1
        s(1)
        input("\nPress Enter To Start The Match... \n")
        s(2)
        print("\n---------- First Innings Begins ----------\n")
        s(2)
        self.play_innings()
        self.batting_team.print_scorecard()
        self.bowling_team.print_bowler_scorecard()
        self.target = self.batting_team.score + 1
        self.innings = 2
        self.batting_team, self.bowling_team = self.bowling_team, self.batting_team
        print(f"\nTarget for {self.batting_team.name}: {self.target}")
        input("Press Enter to Start Second Innings...")
        s(1)
        print("\n---------- Second Innings Begins ----------\n")
        s(2)
        self.play_innings()
        self.batting_team.print_scorecard()
        self.bowling_team.print_bowler_scorecard()

        print("\n--- Match Over ---")
        print(f"{self.home_team.name} scored {self.home_team.score}/{self.home_team.wickets}")
        print(f"{self.away_team.name} scored {self.away_team.score}/{self.away_team.wickets}")
        if self.bowling_team.score > self.batting_team.score:
            margin = self.bowling_team.score - self.batting_team.score
            print(f"{self.home_team.name} won the match by {margin} runs.")
        elif self.batting_team.score > self.bowling_team.score:
            wickets_left = 10 - self.batting_team.wickets
            print(f"{self.batting_team.name} won the match by {wickets_left} wickets.")
        else:
            print("Match Tied!")
            if self.match_format == "T20":
                self.man_of_the_match()
                self.play_super_over()
                if self.top_player:
                    print(f"\n\U0001F3C6 Man of the Match: {self.top_player.name}")
                    print(f"Batting: {self.top_player.runs} runs in {self.top_player.balls} balls")
                    print(f"Bowling: {self.top_player.wickets} wickets, {self.top_player.runs_conceded} runs in {self.top_player.balls_bowled // 6}.{self.top_player.balls_bowled % 6} overs")
                else:
                    print("No standout performance for Man of the Match.")
                return
        self.man_of_the_match()

    def check_follow_on(self, lead, enforce=True):
        print(f"\nLead after first innings: {lead} runs")
        if lead >= self.follow_on_runs:
            enforce = True if input("Do you want to enforce the follow-on? (yes/no): ").lower() == "yes" else False
            choice = "yes" if enforce else "no"
            if choice == "yes":
                print("\nFollow-on enforced!")
                return True
            else:
                print("\nFollow-on not enforced.")
        else:
            print("\nLead is not enough to enforce the follow-on.")
        return False
    
    def check_test_match_draw(self, current_over, max_overs=450):
        if current_over >= max_overs:
            print("\n--- Time is up! Match drawn due to over limit reached. ---")
            return True
        return False


    def play_test_match(self):
        self.match_format = "Test"
        self.follow_on_runs = int(input("Enter the runs to follow on: "))
        # First Innings
        self.toss()
        self.innings = 1
        self.team1_first_innings_session = 1
        self.team2_first_innings_session = 1
        self.team1_second_innings_session = 1
        self.team2_second_innings_session = 1
        s(1)
        input("\nPress Enter To Start the Test Match... \n")
        s(2)
        print("\n---------- 1st Innings Begins ----------\n")
        s(2)
        self.play_innings()
        self.batting_team.print_scorecard()
        self.bowling_team.print_bowler_scorecard()
        team1_first_innings_score = self.batting_team.score
        team1 = self.batting_team
        self.upto_first_innings_overs_bowled = self.overs_bowled

        if self.check_test_match_draw(self.upto_first_innings_overs_bowled, 5*self.overs):
            print("\n--- Test Match Over ---")
            self.man_of_the_match()
            return
        # Second Innings
        self.innings = 2
        self.batting_team, self.bowling_team = self.bowling_team, self.batting_team
        print("\n---------- 2nd Innings Begins ----------\n")
        s(2)
        self.play_innings()
        self.batting_team.print_scorecard()
        self.bowling_team.print_bowler_scorecard()
        team2_first_innings_score = self.batting_team.score
        team2 = self.batting_team
        self.upto_second_innings_overs_bowled = self.upto_first_innings_overs_bowled + self.overs_bowled

        if self.check_test_match_draw(self.upto_second_innings_overs_bowled, 5*self.overs):
            print("\n--- Test Match Over ---")
            self.man_of_the_match()
            return
        
        follow_on_enforced = False
        lead = team1_first_innings_score - team2_first_innings_score
        if lead > 0:
            follow_on_enforced = self.check_follow_on(lead)

        match_ended_early = False

        if follow_on_enforced:
            # Third Innings (follow-on enforced: same team bats again)
            self.innings = 3
            print("\n---------- Follow-On: 3rd Innings Begins ----------\n")
            s(2)
            self.play_innings()
            self.batting_team.print_scorecard()
            self.bowling_team.print_bowler_scorecard()
            team2_second_innings_score = self.batting_team.score
            self.upto_third_innings_overs_bowled = self.upto_second_innings_overs_bowled + self.overs_bowled

            if self.check_test_match_draw(self.upto_third_innings_overs_bowled, 5*self.overs):
                print("\n--- Test Match Over ---")
                self.man_of_the_match()
                return

            if team2_first_innings_score + team2_second_innings_score < team1_first_innings_score:
                print("\n--- Test Match Over ---")
                print(f"{team1.name} won the match by an innings and {team1_first_innings_score - (team2_first_innings_score + team2_second_innings_score)} runs.")
                match_ended_early = True
                self.man_of_the_match()
                return

            # Fourth Innings
            self.innings = 4
            self.batting_team, self.bowling_team = team1, team2
            print("\n---------- 4th Innings Begins ----------\n")
            s(2)
            target = (team2_first_innings_score + team2_second_innings_score) - team1_first_innings_score
            print(f"Target for {self.batting_team.name}: {target + 1}\n")
            self.target = target + 1
            self.play_innings()
            self.batting_team.print_scorecard()
            self.bowling_team.print_bowler_scorecard()
            team1_second_innings_score = self.batting_team.score
            self.upto_fourth_innings_overs_bowled = self.upto_third_innings_overs_bowled + self.overs_bowled

            if self.check_test_match_draw(self.upto_fourth_innings_overs_bowled, 5*self.overs):
                print("\n--- Test Match Over ---")
                self.man_of_the_match()
                return
        else:
            # Third Innings (normal order)
            self.innings = 3
            self.batting_team, self.bowling_team = team1, team2
            print("\n---------- 3rd Innings Begins ----------\n")
            s(2)
            self.play_innings()
            self.batting_team.print_scorecard()
            self.bowling_team.print_bowler_scorecard()
            team1_second_innings_score = self.batting_team.score
            self.upto_third_innings_overs_bowled = self.upto_second_innings_overs_bowled + self.overs_bowled

            if self.check_test_match_draw(self.upto_third_innings_overs_bowled, 5*self.overs):
                print("\n--- Test Match Over ---")
                self.man_of_the_match()
                return

            # Fourth Innings
            self.innings = 4
            self.batting_team, self.bowling_team = team2, team1
            print("\n---------- 4th Innings Begins ----------\n")
            s(2)
            target = (team1_first_innings_score + team1_second_innings_score) - team2_first_innings_score
            print(f"Target for {self.batting_team.name}: {target + 1}\n")
            self.target = target + 1
            self.play_innings()
            self.batting_team.print_scorecard()
            self.bowling_team.print_bowler_scorecard()
            team2_second_innings_score = self.batting_team.score
            self.upto_fourth_innings_overs_bowled = self.upto_third_innings_overs_bowled + self.overs_bowled

            if self.check_test_match_draw(self.upto_fourth_innings_overs_bowled, 5*self.overs):
                print("\n--- Test Match Over ---")
                self.man_of_the_match()
                return

        if not match_ended_early:
            print("\n--- Test Match Over ---")
            team1_total = team1_first_innings_score + team1_second_innings_score
            team2_total = team2_first_innings_score + team2_second_innings_score

            print(f"\n{team1.name} total: {team1_total} ({team1_first_innings_score} & {team1_second_innings_score})")
            print(f"{team2.name} total: {team2_total} ({team2_first_innings_score} & {team2_second_innings_score})")

            if team2_total > team1_total:
                wickets_left = 10 - self.batting_team.wickets
                print(f"{team2.name} won the match by {wickets_left} wickets.")
            elif team1_total > team2_total:
                margin = team1_total - team2_total
                print(f"{team1.name} won the match by {margin} runs.")
            else:
                print("Match Drawn!")
            self.man_of_the_match()


print("Welcome To The Most Advanced Technology For Playing A Cricket Match... \n")
s(1)
match_format = input("Enter the Format of the Match: T20, ODI, Test: ").strip().title()
t1 = input("Enter Home team Name: ")
t1c = input(f"Enter {t1} Captain: ")
t2 = input("Enter Away team Name: ")
t2c = input(f"Enter {t2} Captain: ")

home_team = Team(t1, t1c)
away_team = Team(t2, t2c)

print(f"\nEnter players for {t1}:")
for i in range(11):
    home_team.add_player(Player(input(f"Player {i+1}: ")))

print(f"\nEnter players for {t2}:")
for i in range(11):
    away_team.add_player(Player(input(f"Player {i+1}: ")))

for team in [home_team, away_team]:
    print(f"\nFast bowlers for {team.name}:")
    fast_bowler_No = input("How many fast bowlers?: ")
    if not fast_bowler_No.isdigit():
        print("Invalid input. Please enter a positive integer.")
        fast_bowler_No = input("How many fast bowlers?: ")
    for i in range(int(fast_bowler_No)):
        team.add_fast_bowler(input(f"Name of fast bowler {i+1}: "))
    print(f"\nSpin bowlers for {team.name}:")
    spin_bowler_No = input("How many Spin bowlers?: ")
    if not spin_bowler_No.isdigit():
        print("Invalid input. Please enter a positive integer.")
        spin_bowler_No = input("How many spin bowlers?: ")
    for i in range(int(spin_bowler_No)):
        team.add_spin_bowler(input(f"Name of spin bowler {i+1}: "))

overs = int(input("\nEnter number of overs: "))
match = Match(overs, home_team, away_team)
match.play_match(match_format)
