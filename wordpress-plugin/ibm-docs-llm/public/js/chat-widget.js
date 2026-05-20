(function($) {
    'use strict';
    
    class IBMDocsChat {
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
            const $widget = $('#ibm-docs-chat-widget');
            if ($widget.hasClass('floating')) {
                $widget.find('.chat-container').hide();
            }
        }
        
        bindEvents() {
            // Form submission
            $('#ibm-docs-chat-form').on('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
            
            // Toggle widget
            $('#ibm-docs-chat-toggle').on('click', () => {
                this.toggleChat();
            });
            
            // Minimize widget
            $('#ibm-docs-chat-minimize').on('click', () => {
                this.minimizeChat();
            });
            
            // Close widget
            $('#ibm-docs-chat-close').on('click', () => {
                this.closeChat();
            });
            
            // Enter key to send
            $('#ibm-docs-chat-input').on('keypress', (e) => {
                if (e.which === 13 && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        async sendMessage() {
            if (this.isLoading) return;
            
            const $input = $('#ibm-docs-chat-input');
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
                    this.displayError(response.data.message || ibmDocsLLM.strings.error);
                }
                
            } catch (error) {
                console.error('Chat error:', error);
                this.displayError(ibmDocsLLM.strings.error);
            } finally {
                this.isLoading = false;
                this.hideLoading();
            }
        }
        
        async callAPI(question) {
            // Use WordPress REST API
            const response = await $.ajax({
                url: ibmDocsLLM.ajaxUrl,
                method: 'POST',
                data: {
                    action: 'ibm_docs_llm_chat',
                    nonce: ibmDocsLLM.nonce,
                    question: question,
                    conversation_id: this.conversationId
                }
            });
            
            return response;
        }
        
        displayMessage(text, role, sources = null) {
            const $messages = $('#ibm-docs-chat-messages');
            
            const messageHtml = `
                <div class="chat-message chat-message-${role}">
                    <div class="message-content">${this.escapeHtml(text)}</div>
                    ${sources ? this.renderSources(sources) : ''}
                </div>
            `;
            
            $messages.append(messageHtml);
            this.scrollToBottom();
        }
        
        renderSources(sources) {
            if (!sources || sources.length === 0) return '';
            
            let html = `<div class="message-sources">
                <strong>${ibmDocsLLM.strings.sources}</strong>
                <ul>`;
            
            sources.forEach(source => {
                html += `
                    <li>
                        <a href="${this.escapeHtml(source.url)}" target="_blank" rel="noopener">
                            ${this.escapeHtml(source.title)}
                        </a>
                        <span class="source-score">(${(source.relevance_score * 100).toFixed(0)}%)</span>
                    </li>
                `;
            });
            
            html += '</ul></div>';
            return html;
        }
        
        displayError(message) {
            const $messages = $('#ibm-docs-chat-messages');
            
            const errorHtml = `
                <div class="chat-message chat-message-error">
                    <div class="message-content">${this.escapeHtml(message)}</div>
                </div>
            `;
            
            $messages.append(errorHtml);
            this.scrollToBottom();
        }
        
        showLoading() {
            $('#ibm-docs-chat-loading').show();
            $('#ibm-docs-chat-submit').prop('disabled', true);
        }
        
        hideLoading() {
            $('#ibm-docs-chat-loading').hide();
            $('#ibm-docs-chat-submit').prop('disabled', false);
        }
        
        toggleChat() {
            const $container = $('#ibm-docs-chat-container');
            const $toggle = $('#ibm-docs-chat-toggle');
            
            if ($container.is(':visible')) {
                $container.slideUp(300);
                $toggle.removeClass('active');
            } else {
                $container.slideDown(300);
                $toggle.addClass('active');
                $('#ibm-docs-chat-input').focus();
            }
        }
        
        minimizeChat() {
            $('#ibm-docs-chat-container').slideUp(300);
            $('#ibm-docs-chat-toggle').removeClass('active');
        }
        
        closeChat() {
            this.minimizeChat();
        }
        
        scrollToBottom() {
            const $messages = $('#ibm-docs-chat-messages');
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
        if ($('#ibm-docs-chat-widget').length) {
            new IBMDocsChat();
        }
    });
    
})(jQuery);

// Made with Bob
