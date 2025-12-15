/**
 * Help Desk - Main JavaScript (jQuery)
 * This file contains jQuery enhancements for the Help Desk application
 */

$(document).ready(function() {
    
    // ===========================================
    // Global jQuery Enhancements
    // ===========================================
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Add animation to cards on page load
    $('.card').each(function(index) {
        $(this).css('opacity', 0);
        $(this).delay(100 * index).animate({ opacity: 1 }, 300);
    });
    
    // ===========================================
    // Form Validation Enhancements
    // ===========================================
    
    // Password confirmation validation
    $('#confirm_password').on('keyup', function() {
        var password = $('#password').val();
        var confirmPassword = $(this).val();
        
        if (password !== confirmPassword) {
            $(this).addClass('is-invalid');
        } else {
            $(this).removeClass('is-invalid').addClass('is-valid');
        }
    });
    
    // Email validation on blur
    $('input[type="email"]').on('blur', function() {
        var email = $(this).val();
        var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (email && !emailRegex.test(email)) {
            $(this).addClass('is-invalid');
        } else if (email) {
            $(this).removeClass('is-invalid').addClass('is-valid');
        }
    });
    
    // ===========================================
    // Table Interactions
    // ===========================================
    
    // Highlight table row on hover
    $('table.table-hover tbody tr').hover(
        function() {
            $(this).css('cursor', 'pointer');
        },
        function() {
            $(this).css('cursor', 'default');
        }
    );
    
    // Click on table row to navigate (except action column)
    $('table.table tbody tr').on('click', function(e) {
        // Don't trigger if clicking on buttons, links, or form elements
        if ($(e.target).is('a, button, select, input') || $(e.target).closest('form').length) {
            return;
        }
        
        var link = $(this).find('td a').first().attr('href');
        if (link) {
            window.location.href = link;
        }
    });
    
    // ===========================================
    // Filter Form Enhancements
    // ===========================================
    
    // Show loading indicator on form submit
    $('form').on('submit', function() {
        var $btn = $(this).find('button[type="submit"]');
        if (!$btn.data('no-loading')) {
            $btn.prop('disabled', true);
            $btn.html('<span class="spinner-border spinner-border-sm me-1"></span>Loading...');
        }
    });
    
    // ===========================================
    // Character Counter for Textareas
    // ===========================================
    
    $('textarea[maxlength]').each(function() {
        var maxLength = $(this).attr('maxlength');
        var $counter = $('<small class="text-muted float-end"></small>');
        $(this).after($counter);
        
        $(this).on('input', function() {
            var remaining = maxLength - $(this).val().length;
            $counter.text(remaining + ' characters remaining');
        });
    });
    
    // ===========================================
    // Confirmation Dialogs
    // ===========================================
    
    // Confirm delete actions
    $('form[data-confirm]').on('submit', function(e) {
        var message = $(this).data('confirm') || 'Are you sure you want to proceed?';
        if (!confirm(message)) {
            e.preventDefault();
        }
    });
    
    // ===========================================
    // Keyboard Shortcuts
    // ===========================================
    
    $(document).on('keydown', function(e) {
        // Ctrl/Cmd + N = New Ticket
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            var newTicketUrl = $('a[href*="tickets/new"]').attr('href');
            if (newTicketUrl) {
                window.location.href = newTicketUrl;
            }
        }
        
        // Escape = Close modals/alerts
        if (e.key === 'Escape') {
            $('.alert .btn-close').click();
            $('.modal').modal('hide');
        }
    });
    
    // ===========================================
    // Tooltips Initialization
    // ===========================================
    
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // ===========================================
    // Scroll to Top Button
    // ===========================================
    
    // Add scroll to top button
    var $scrollTopBtn = $('<button id="scrollTopBtn" class="btn btn-primary btn-sm position-fixed" style="bottom: 20px; right: 20px; display: none; z-index: 1000;"><i class="bi bi-arrow-up"></i></button>');
    $('body').append($scrollTopBtn);
    
    $(window).scroll(function() {
        if ($(this).scrollTop() > 200) {
            $scrollTopBtn.fadeIn();
        } else {
            $scrollTopBtn.fadeOut();
        }
    });
    
    $scrollTopBtn.on('click', function() {
        $('html, body').animate({ scrollTop: 0 }, 'fast');
    });
    
    // ===========================================
    // Search Highlight (for filtered results)
    // ===========================================
    
    function highlightSearchTerm() {
        var searchParam = new URLSearchParams(window.location.search).get('search');
        if (searchParam) {
            $('table tbody td').each(function() {
                var $td = $(this);
                var text = $td.text();
                var regex = new RegExp('(' + searchParam.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
                if (regex.test(text)) {
                    $td.html($td.text().replace(regex, '<mark>$1</mark>'));
                }
            });
        }
    }
    
    highlightSearchTerm();
    
    // ===========================================
    // Print Functionality
    // ===========================================
    
    // Add print button for ticket detail
    if ($('.ticket-detail').length || $('h2:contains("Ticket #")').length) {
        var $printBtn = $('<button class="btn btn-outline-secondary btn-sm ms-2"><i class="bi bi-printer"></i> Print</button>');
        $('h2').first().after($printBtn);
        
        $printBtn.on('click', function() {
            window.print();
        });
    }
    
    // ===========================================
    // Console welcome message
    // ===========================================
    
    console.log('%c Help Desk System ', 'background: #0d6efd; color: white; font-size: 16px; padding: 10px;');
    console.log('COMP 2053 - Final Project');
    
});
