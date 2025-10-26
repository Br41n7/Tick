// Main JavaScript for Tick Entertainment Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// AJAX Functions
function ajaxRequest(url, method = 'GET', data = null) {
    const csrfToken = getCookie('csrftoken');
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    if (data && method !== 'GET') {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Event Booking
function bookEvent(eventId, quantity = 1) {
    const data = { quantity: quantity };
    
    ajaxRequest('/events/ajax/book/' + eventId + '/', 'POST', data)
        .then(response => {
            if (response.success) {
                // Redirect to payment page
                window.location.href = response.payment_url;
            } else {
                showAlert(response.message, 'danger');
            }
        })
        .catch(error => {
            showAlert('An error occurred. Please try again.', 'danger');
            console.error('Error:', error);
        });
}

// Favorite Event
function toggleFavorite(eventId, button) {
    ajaxRequest('/events/ajax/favorite/' + eventId + '/', 'POST')
        .then(response => {
            if (response.success) {
                updateFavoriteButton(button, response.is_favorited);
                updateFavoriteCount(button, response.favorite_count);
                showAlert(response.is_favorited ? 'Event added to favorites!' : 'Event removed from favorites!', 'success');
            }
        })
        .catch(error => {
            showAlert('An error occurred. Please try again.', 'danger');
            console.error('Error:', error);
        });
}

// Follow Artist
function toggleFollow(artistId, button) {
    ajaxRequest('/artists/ajax/follow/' + artistId + '/', 'POST')
        .then(response => {
            if (response.success) {
                updateFollowButton(button, response.is_following);
                updateFollowCount(button, response.follower_count);
                showAlert(response.is_following ? 'Artist followed!' : 'Artist unfollowed!', 'success');
            }
        })
        .catch(error => {
            showAlert('An error occurred. Please try again.', 'danger');
            console.error('Error:', error);
        });
}

// Like Reel
function toggleLike(reelId, button) {
    ajaxRequest('/artists/ajax/like/' + reelId + '/', 'POST')
        .then(response => {
            if (response.success) {
                updateLikeButton(button, response.is_liked);
                updateLikeCount(button, response.like_count);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Track Reel View
function trackReelView(reelId) {
    ajaxRequest('/artists/ajax/view/' + reelId + '/', 'POST')
        .catch(error => {
            console.error('Error tracking view:', error);
        });
}

// Helper Functions
function updateFavoriteButton(button, isFavorited) {
    if (isFavorited) {
        button.innerHTML = '<i class="bi bi-heart-fill"></i> Favorited';
        button.classList.remove('btn-outline-primary');
        button.classList.add('btn-primary');
    } else {
        button.innerHTML = '<i class="bi bi-heart"></i> Favorite';
        button.classList.remove('btn-primary');
        button.classList.add('btn-outline-primary');
    }
}

function updateFavoriteCount(button, count) {
    const countElement = button.closest('.card').querySelector('.favorite-count');
    if (countElement) {
        countElement.textContent = count;
    }
}

function updateFollowButton(button, isFollowing) {
    if (isFollowing) {
        button.innerHTML = '<i class="bi bi-person-check-fill"></i> Following';
        button.classList.remove('btn-outline-primary');
        button.classList.add('btn-primary');
    } else {
        button.innerHTML = '<i class="bi bi-person-plus"></i> Follow';
        button.classList.remove('btn-primary');
        button.classList.add('btn-outline-primary');
    }
}

function updateFollowCount(button, count) {
    const countElement = button.closest('.artist-card')?.querySelector('.follower-count');
    if (countElement) {
        countElement.textContent = count.toLocaleString() + ' followers';
    }
}

function updateLikeButton(button, isLiked) {
    const icon = button.querySelector('i');
    if (isLiked) {
        icon.classList.remove('bi-heart');
        icon.classList.add('bi-heart-fill');
        button.classList.add('text-danger');
    } else {
        icon.classList.remove('bi-heart-fill');
        icon.classList.add('bi-heart');
        button.classList.remove('text-danger');
    }
}

function updateLikeCount(button, count) {
    const countElement = button.closest('.reel-card')?.querySelector('.like-count');
    if (countElement) {
        countElement.textContent = count;
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Load more content (infinite scroll)
function loadMoreContent(url, containerId, buttonId) {
    const button = document.getElementById(buttonId);
    const container = document.getElementById(containerId);
    const currentPage = parseInt(button.dataset.page) || 1;
    
    button.innerHTML = '<span class="loading"></span> Loading...';
    button.disabled = true;
    
    ajaxRequest(url + '?page=' + (currentPage + 1))
        .then(response => {
            if (response.html) {
                container.insertAdjacentHTML('beforeend', response.html);
                button.dataset.page = currentPage + 1;
                
                if (!response.has_more) {
                    button.style.display = 'none';
                }
            }
        })
        .catch(error => {
            showAlert('Failed to load more content.', 'danger');
        })
        .finally(() => {
            button.innerHTML = 'Load More';
            button.disabled = false;
        });
}

// Search with live results
function setupLiveSearch(inputId, resultsContainerId, searchUrl) {
    const input = document.getElementById(inputId);
    const resultsContainer = document.getElementById(resultsContainerId);
    let debounceTimer;
    
    input.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const query = this.value.trim();
        
        if (query.length < 2) {
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'none';
            return;
        }
        
        debounceTimer = setTimeout(() => {
            ajaxRequest(searchUrl + '?q=' + encodeURIComponent(query))
                .then(response => {
                    if (response.html) {
                        resultsContainer.innerHTML = response.html;
                        resultsContainer.style.display = 'block';
                    } else {
                        resultsContainer.innerHTML = '<div class="p-3">No results found</div>';
                        resultsContainer.style.display = 'block';
                    }
                })
                .catch(error => {
                    console.error('Search error:', error);
                });
        }, 300);
    });
    
    // Hide results when clicking outside
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.style.display = 'none';
        }
    });
}

// Image upload preview
function setupImagePreview(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    
    input.addEventListener('change', function() {
        const file = this.files[0];
        if (file && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
}