// API Configuration
// Change this to your deployed backend URL when hosting
const API_BASE_URL = window.API_BASE_URL || 'http://localhost:8000';

// Game State
let gameState = {
    gameId: null,
    playerId: null,
    playerName: null,
    isPlayer1: false,
    opponentName: null,
    currentTurn: null,
    status: 'waiting',
    pollingInterval: null
};

// DOM Elements
const screens = {
    home: document.getElementById('home-screen'),
    lobby: document.getElementById('lobby-screen'),
    game: document.getElementById('game-screen'),
    result: document.getElementById('result-screen')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

// Event Listeners Setup
function setupEventListeners() {
    // Home Screen
    document.getElementById('create-game-btn').addEventListener('click', createGame);
    document.getElementById('join-game-btn').addEventListener('click', joinGame);
    
    // Lobby Screen
    document.getElementById('copy-game-id').addEventListener('click', copyGameId);
    document.getElementById('lock-number-btn').addEventListener('click', lockNumber);
    
    // Game Screen
    document.getElementById('submit-guess-btn').addEventListener('click', submitGuess);
    document.getElementById('guess-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') submitGuess();
    });
    
    // Result Screen
    document.getElementById('play-again-btn').addEventListener('click', playAgain);
    
    // Input validation - only allow digits
    document.getElementById('secret-number').addEventListener('input', validateDigitInput);
    document.getElementById('guess-input').addEventListener('input', validateDigitInput);
}

// Validate digit-only input
function validateDigitInput(e) {
    e.target.value = e.target.value.replace(/[^0-9]/g, '');
}

// Screen Navigation
function showScreen(screenName) {
    Object.values(screens).forEach(screen => screen.classList.remove('active'));
    screens[screenName].classList.add('active');
}

// Toast Notification
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// API Calls
async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Create Game
async function createGame() {
    const playerName = document.getElementById('player-name').value.trim();
    
    if (!playerName) {
        showToast('Please enter your name', 'error');
        return;
    }
    
    try {
        const data = await apiCall('/games', 'POST', { player_name: playerName });
        
        gameState.gameId = data.game_id;
        gameState.playerId = data.player_id;
        gameState.playerName = playerName;
        gameState.isPlayer1 = true;
        
        showToast('Game created! Share the Game ID with your friend', 'success');
        updateLobbyUI();
        showScreen('lobby');
        startPolling();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Join Game
async function joinGame() {
    const playerName = document.getElementById('player-name').value.trim();
    const gameId = document.getElementById('game-id-input').value.trim();
    
    if (!playerName) {
        showToast('Please enter your name', 'error');
        return;
    }
    
    if (!gameId) {
        showToast('Please enter a Game ID', 'error');
        return;
    }
    
    try {
        const data = await apiCall(`/games/${gameId}/join`, 'POST', { player_name: playerName });
        
        gameState.gameId = data.game_id;
        gameState.playerId = data.player_id;
        gameState.playerName = playerName;
        gameState.isPlayer1 = false;
        
        showToast('Joined game successfully!', 'success');
        updateLobbyUI();
        showScreen('lobby');
        startPolling();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Copy Game ID
function copyGameId() {
    const gameId = document.getElementById('display-game-id').textContent;
    navigator.clipboard.writeText(gameId).then(() => {
        showToast('Game ID copied to clipboard!', 'success');
    });
}

// Lock Number
async function lockNumber() {
    const secretNumber = document.getElementById('secret-number').value.trim();
    
    if (!secretNumber || secretNumber.length !== 4) {
        showToast('Please enter a 4-digit number', 'error');
        return;
    }
    
    try {
        const data = await apiCall(
            `/games/${gameState.gameId}/players/${gameState.playerId}/lock-number`,
            'POST',
            { secret_number: secretNumber }
        );
        
        showToast('Number locked!', 'success');
        
        document.getElementById('lock-number-section').classList.add('hidden');
        document.getElementById('waiting-message').classList.remove('hidden');
        
        // Update player status
        if (gameState.isPlayer1) {
            updatePlayerStatus('player1', true);
        } else {
            updatePlayerStatus('player2', true);
        }
        
        // Check if game started
        if (data.game_status === 'in_progress') {
            startGame();
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Update Lobby UI
function updateLobbyUI() {
    document.getElementById('display-game-id').textContent = gameState.gameId;
    
    if (gameState.isPlayer1) {
        document.getElementById('player1-name').textContent = gameState.playerName;
        document.getElementById('player2-name').textContent = 'Waiting...';
    } else {
        document.getElementById('player2-name').textContent = gameState.playerName;
    }
}

// Update Player Status
function updatePlayerStatus(player, isReady) {
    const statusEl = document.getElementById(`${player}-status`);
    statusEl.textContent = isReady ? 'Ready!' : 'Waiting...';
    statusEl.className = `status ${isReady ? 'ready' : 'waiting'}`;
}

// Start Polling for Game Updates
function startPolling() {
    if (gameState.pollingInterval) {
        clearInterval(gameState.pollingInterval);
    }
    
    gameState.pollingInterval = setInterval(async () => {
        try {
            const data = await apiCall(`/games/${gameState.gameId}`);
            
            // Update player names
            document.getElementById('player1-name').textContent = data.player_1.name;
            updatePlayerStatus('player1', data.player_1.is_ready);
            
            if (data.player_2) {
                document.getElementById('player2-name').textContent = data.player_2.name;
                updatePlayerStatus('player2', data.player_2.is_ready);
                
                // Store opponent name
                if (gameState.isPlayer1) {
                    gameState.opponentName = data.player_2.name;
                } else {
                    gameState.opponentName = data.player_1.name;
                }
            }
            
            // Check game status
            if (data.status === 'in_progress' && gameState.status !== 'in_progress') {
                gameState.status = 'in_progress';
                gameState.currentTurn = data.current_turn;
                startGame();
            }
            
            if (data.status === 'completed') {
                gameState.status = 'completed';
                stopPolling();
                showResult(data);
            }
            
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 2000);
}

// Stop Polling
function stopPolling() {
    if (gameState.pollingInterval) {
        clearInterval(gameState.pollingInterval);
        gameState.pollingInterval = null;
    }
}

// Start Game
function startGame() {
    stopPolling();
    showScreen('game');
    updateTurnIndicator();
    startGamePolling();
}

// Start Game Polling (for turn updates)
function startGamePolling() {
    gameState.pollingInterval = setInterval(async () => {
        try {
            const data = await apiCall(`/games/${gameState.gameId}`);
            
            gameState.currentTurn = data.current_turn;
            gameState.status = data.status;
            
            document.getElementById('turn-count').textContent = data.turn_count;
            updateTurnIndicator();
            
            // Refresh guess history
            await refreshGuessHistory();
            
            if (data.status === 'completed') {
                stopPolling();
                showResult(data);
            }
            
        } catch (error) {
            console.error('Game polling error:', error);
        }
    }, 2000);
}

// Update Turn Indicator
function updateTurnIndicator() {
    const indicator = document.getElementById('turn-indicator');
    const guessSection = document.getElementById('guess-section');
    const isMyTurn = gameState.currentTurn === gameState.playerId;
    
    if (isMyTurn) {
        indicator.textContent = 'Your Turn';
        indicator.className = 'turn-indicator your-turn';
        guessSection.classList.remove('hidden');
        document.getElementById('guess-input').disabled = false;
        document.getElementById('submit-guess-btn').disabled = false;
    } else {
        indicator.textContent = "Opponent's Turn";
        indicator.className = 'turn-indicator opponent-turn';
        document.getElementById('guess-input').disabled = true;
        document.getElementById('submit-guess-btn').disabled = true;
    }
}

// Submit Guess
async function submitGuess() {
    const guessInput = document.getElementById('guess-input');
    const guess = guessInput.value.trim();
    
    if (!guess || guess.length !== 4) {
        showToast('Please enter a 4-digit guess', 'error');
        return;
    }
    
    try {
        const data = await apiCall(`/games/${gameState.gameId}/guess`, 'POST', {
            player_id: gameState.playerId,
            guessed_number: guess
        });
        
        guessInput.value = '';
        
        // Update turn count
        document.getElementById('turn-count').textContent = data.turn_number;
        
        // Add to history
        addGuessToHistory({
            turn_number: data.turn_number,
            guesser: gameState.playerName,
            guessed_number: data.guessed_number,
            correct_digits: data.correct_digits,
            correct_positions: data.correct_positions,
            isYours: true
        });
        
        // Update your guesses count
        updateYourGuessesCount();
        
        if (data.is_winner) {
            stopPolling();
            showWinResult();
        } else {
            gameState.currentTurn = data.next_turn;
            updateTurnIndicator();
            showToast(`CD: ${data.correct_digits}, CP: ${data.correct_positions}`, 'info');
        }
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Refresh Guess History
async function refreshGuessHistory() {
    try {
        const data = await apiCall(`/games/${gameState.gameId}/guesses`);
        
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '';
        
        let yourGuesses = 0;
        
        data.guesses.forEach(guess => {
            const isYours = (gameState.isPlayer1 && guess.guesser === document.getElementById('player1-name').textContent) ||
                           (!gameState.isPlayer1 && guess.guesser === document.getElementById('player2-name').textContent);
            
            if (isYours) yourGuesses++;
            
            addGuessToHistory({
                turn_number: guess.turn_number,
                guesser: guess.guesser,
                guessed_number: guess.guessed_number,
                correct_digits: guess.correct_digits,
                correct_positions: guess.correct_positions,
                isYours: isYours
            }, false);
        });
        
        document.getElementById('your-guesses-count').textContent = yourGuesses;
        
    } catch (error) {
        console.error('Error refreshing history:', error);
    }
}

// Add Guess to History
function addGuessToHistory(guess, prepend = true) {
    const historyList = document.getElementById('history-list');
    
    const item = document.createElement('div');
    item.className = `history-item ${guess.isYours ? 'your-guess' : 'opponent-guess'}`;
    
    item.innerHTML = `
        <div class="guess-info">
            <span class="turn-num">#${guess.turn_number}</span>
            <span class="guesser">${guess.guesser}</span>
            <span class="guess-number">${guess.guessed_number}</span>
        </div>
        <div class="results">
            <span class="result-badge cd">CD: ${guess.correct_digits}</span>
            <span class="result-badge cp">CP: ${guess.correct_positions}</span>
        </div>
    `;
    
    if (prepend) {
        historyList.insertBefore(item, historyList.firstChild);
    } else {
        historyList.appendChild(item);
    }
}

// Update Your Guesses Count
function updateYourGuessesCount() {
    const currentCount = parseInt(document.getElementById('your-guesses-count').textContent);
    document.getElementById('your-guesses-count').textContent = currentCount + 1;
}

// Show Win Result
function showWinResult() {
    document.getElementById('result-title').textContent = 'You Won!';
    document.getElementById('result-title').className = 'win';
    document.getElementById('winner-display').textContent = '🎉🏆🎉';
    document.getElementById('result-message').textContent = 'Congratulations! You guessed the correct number!';
    document.getElementById('final-turns').textContent = document.getElementById('turn-count').textContent;
    
    showScreen('result');
}

// Show Result
function showResult(gameData) {
    const isWinner = gameData.winner_id === gameState.playerId;
    
    if (isWinner) {
        document.getElementById('result-title').textContent = 'You Won!';
        document.getElementById('result-title').className = 'win';
        document.getElementById('winner-display').textContent = '🎉🏆🎉';
        document.getElementById('result-message').textContent = 'Congratulations! You guessed the correct number!';
    } else {
        document.getElementById('result-title').textContent = 'You Lost!';
        document.getElementById('result-title').className = 'lose';
        document.getElementById('winner-display').textContent = '😔';
        document.getElementById('result-message').textContent = `${gameState.opponentName || 'Your opponent'} guessed your number!`;
    }
    
    document.getElementById('final-turns').textContent = gameData.turn_count;
    showScreen('result');
}

// Play Again
function playAgain() {
    // Reset game state
    gameState = {
        gameId: null,
        playerId: null,
        playerName: null,
        isPlayer1: false,
        opponentName: null,
        currentTurn: null,
        status: 'waiting',
        pollingInterval: null
    };
    
    // Reset UI
    document.getElementById('player-name').value = '';
    document.getElementById('game-id-input').value = '';
    document.getElementById('secret-number').value = '';
    document.getElementById('guess-input').value = '';
    document.getElementById('history-list').innerHTML = '';
    document.getElementById('lock-number-section').classList.remove('hidden');
    document.getElementById('waiting-message').classList.add('hidden');
    document.getElementById('turn-count').textContent = '0';
    document.getElementById('your-guesses-count').textContent = '0';
    
    showScreen('home');
}
