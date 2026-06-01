(function($) {
    'use strict';
    
    class FahmFarisChat {
        constructor() {
            this.conversationId = null;
            this.isLoading = false;
            this.init();
        }
        
        init() {
            this.bindEvents();
            this.initWidget();
        }
        
        initWidget() {
            // Set initial state
            const $widget = $('#fahm-faris-chat-widget');
            if ($widget.hasClass('floating')) {
                $widget.find('.chat-container').hide();
                
                // Show prompt bubble after 2 seconds if not dismissed before
                setTimeout(() => {
                    const promptDismissed = localStorage.getItem('fahmFarisPromptDismissed');
                    if (!promptDismissed) {
                        $('#fahm-faris-chat-prompt').fadeIn(300);
                    }
                }, 2000);
            }
        }
        
        bindEvents() {
            // Form submission
            $('#fahm-faris-chat-form').on('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
            
            // Toggle widget
            $('#fahm-faris-chat-toggle').on('click', () => {
                this.toggleChat();
                this.hidePrompt();
            });
            
            // Click on prompt bubble to open chat
            $('#fahm-faris-chat-prompt').on('click', () => {
                this.toggleChat();
                this.dismissPrompt();
            });
            
            // Minimize widget
            $('#fahm-faris-chat-minimize').on('click', () => {
                this.minimizeChat();
            });
            
            // Close widget
            $('#fahm-faris-chat-close').on('click', () => {
                this.closeChat();
            });
            
            // Enter key to send
            $('#fahm-faris-chat-input').on('keypress', (e) => {
                if (e.which === 13 && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        async sendMessage() {
            if (this.isLoading) return;
            
            const $input = $('#fahm-faris-chat-input');
            const question = $input.val().trim();
            
            if (!question) return;
            
            this.isLoading = true;
            this.showLoading();
            
            // Display user message
            this.displayMessage(question, 'user');
            $input.val('');
            
            try {
                const response = await this.callAPI(question);
                
                if (response.success) {
                    const data = response.data;
                    this.conversationId = data.conversation_id;
                    this.displayMessage(data.answer, 'assistant', data.sources);
                } else {
                    this.displayError(response.data.message || fahmFaris.strings.error);
                }
                
            } catch (error) {
                console.error('Chat error:', error);
                this.displayError(fahmFaris.strings.error);
            } finally {
                this.isLoading = false;
                this.hideLoading();
            }
        }
        
        async callAPI(question) {
            // Use WordPress REST API
            const response = await $.ajax({
                url: fahmFaris.ajaxUrl,
                method: 'POST',
                data: {
                    action: 'fahm_faris_chat',
                    nonce: fahmFaris.nonce,
                    question: question,
                    conversation_id: this.conversationId
                }
            });
            
            return response;
        }
        
        displayMessage(text, role, sources = null) {
            const $messages = $('#fahm-faris-chat-messages');
            
            const messageHtml = `
                <div class="chat-message chat-message-${role}">
                    <div class="message-content">${this.escapeHtml(text)}</div>
                </div>
            `;
            
            $messages.append(messageHtml);
            this.scrollToBottom();
        }
        

        
        displayError(message) {
            const $messages = $('#fahm-faris-chat-messages');
            
            const errorHtml = `
                <div class="chat-message chat-message-error">
                    <div class="message-content">${this.escapeHtml(message)}</div>
                </div>
            `;
            
            $messages.append(errorHtml);
            this.scrollToBottom();
        }
        
        showLoading() {
            $('#fahm-faris-chat-loading').show();
            $('#fahm-faris-chat-submit').prop('disabled', true);
        }
        
        hideLoading() {
            $('#fahm-faris-chat-loading').hide();
            $('#fahm-faris-chat-submit').prop('disabled', false);
        }
        
        toggleChat() {
            const $container = $('#fahm-faris-chat-container');
            const $toggle = $('#fahm-faris-chat-toggle');
            
            if ($container.is(':visible')) {
                $container.slideUp(300);
                $toggle.removeClass('active');
            } else {
                $container.slideDown(300);
                $toggle.addClass('active');
                $('#fahm-faris-chat-input').focus();
            }
        }
        
        minimizeChat() {
            $('#fahm-faris-chat-container').slideUp(300);
            $('#fahm-faris-chat-toggle').removeClass('active');
        }
        
        closeChat() {
            $('#fahm-faris-chat-container').slideUp(300);
            $('#fahm-faris-chat-toggle').removeClass('active');
        }
        
        hidePrompt() {
            $('#fahm-faris-chat-prompt').fadeOut(300);
        }
        
        dismissPrompt() {
            this.hidePrompt();
            localStorage.setItem('fahmFarisPromptDismissed', 'true');
        }
        

            $('#fahm-faris-chat-toggle').removeClass('active');
        }
        
        closeChat() {
            this.minimizeChat();
        }
        
        scrollToBottom() {
            const $messages = $('#fahm-faris-chat-messages');
            $messages.animate({
                scrollTop: $messages[0].scrollHeight
            }, 300);
        }
        
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    }
    
    // Initialize when document is ready
    $(document).ready(function() {
        if ($('#fahm-faris-chat-widget').length) {
            new FahmFarisChat();
        }
    });
    
})(jQuery);

// Made with Bob
