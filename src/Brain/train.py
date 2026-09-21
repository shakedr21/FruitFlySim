import torch
import torch.optim as optim

from src.common.consts import subnetwork_csv_path, trained_model_output_path, model_beta_value
from src.scripts.input_output_ids_helper import get_inupt_ids, get_output_ids

from FlyBrainSNN import FlyBrainSNN
from game_wrapper import GameWrapperObject
from connectome_to_tensor import load_connectome_to_tensors

if __name__ == "__main__":
    # 1. Load data and instantiate model
    W, M, input_idx, output_idx, N = load_connectome_to_tensors(
        subnetwork_csv_path,
        get_inupt_ids(),
        get_output_ids()
    )

    brain = FlyBrainSNN(W, M, input_idx, output_idx, beta=model_beta_value)
    optimizer = optim.Adam(brain.parameters(), lr=1e-3)
    game = GameWrapperObject()

    # 2. Training Loop
    best_score = 0.0
    num_episodes = 500

    for episode in range(num_episodes):
        game.reset()
        done = False

        log_probs = []
        rewards = []

        while not done:
            # Encode state into 80 input currents
            input_currents = game.get_input_currents()

            # Run SNN for 16 discrete time steps
            total_gf_spikes = brain(input_currents, steps=16)

            # Convert total Giant Fiber spikes to action probability (Flap vs Do Nothing)
            # Higher spike count increases the logit for jumping
            flap_logit = total_gf_spikes - 2.0  # Threshold offset
            action_prob = torch.sigmoid(flap_logit)

            # Sample action (Bernoulli distribution)
            dist = torch.distributions.Bernoulli(action_prob)
            action = dist.sample()  # 1 = Jump, 0 = Do Nothing

            # Store log probability for Policy Gradient update
            log_probs.append(dist.log_prob(action))

            # Execute turn in your game engine
            reward, done = game.step(int(action.item()))
            rewards.append(reward)

        # --- POLICY GRADIENT UPDATE (REINFORCE) ---
        # Compute discounted returns
        discounted_returns = []
        R = 0
        gamma = 0.99
        for r in reversed(rewards):
            R = r + gamma * R
            discounted_returns.insert(0, R)

        returns = torch.tensor(discounted_returns, dtype=torch.float32)
        # Normalize returns for training stability
        if len(returns) > 1:
            returns = (returns - returns.mean()) / (returns.std() + 1e-8)

        # Compute policy loss
        policy_loss = []
        for log_prob, R in zip(log_probs, returns):
            policy_loss.append(-log_prob * R)

        optimizer.zero_grad()
        total_loss = torch.stack(policy_loss).sum()
        total_loss.backward()  # Backpropagates through time and surrogate gradients
        optimizer.step()

        current_score = sum(rewards)
        print(f"Episode {episode} | Total Score: {current_score:.1f}")

        if current_score > best_score:
            best_score = current_score

            # Save the weights to a file
            torch.save(brain.state_dict(), trained_model_output_path)
            print(f"   -> New high score! Brain saved to disk.")
