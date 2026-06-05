<?php
/**
 * Widget class for Fahm Faris
 */

class Fahm_Faris_Widget {
    
    /**
     * Initialize widget
     */
    public static function init() {
        add_action('wp_footer', array(__CLASS__, 'render_floating_widget'));
    }
    
    /**
     * Render floating widget
     */
    public static function render_floating_widget() {
        if (!get_option('fahm_faris_enable_widget', true)) {
            return;
        }
        
        $title = get_option('fahm_faris_widget_title', __('Chat with Faris', 'fahm-faris'));
        $placeholder = get_option('fahm_faris_placeholder', __('Ask me anything about FAHM...', 'fahm-faris'));
        $position = get_option('fahm_faris_position', 'bottom-right');
        
        self::render_widget_html($title, $placeholder, true, $position);
    }
    
    /**
     * Render widget HTML - Exact match to demo
     */
    public static function render_widget_html($title, $placeholder, $floating = false, $position = 'bottom-right') {
        $widget_class = 'fahm-faris-chat-widget';
        if ($floating) {
            $widget_class .= ' floating position-' . esc_attr($position);
        }
        ?>
        <div id="fahm-faris-chat-widget" class="<?php echo esc_attr($widget_class); ?>">
            <!-- Prompt Bubble -->
            <div class="chat-prompt" id="fahm-faris-chat-prompt">
                <div class="prompt-bubble">
                    <span class="prompt-text">👋 Hey there! I'm Faris, your FAHM guide!</span>
                    <button class="prompt-close" id="fahm-faris-prompt-close">×</button>
                </div>
            </div>

            <!-- Chat Toggle Button -->
            <div class="chat-toggle" id="fahm-faris-chat-toggle">
                🧙‍♂️
            </div>

            <!-- Chat Container -->
            <div class="chat-container" id="fahm-faris-chat-container">
                <div class="chat-header">
                    <h3><?php echo esc_html($title); ?></h3>
                    <div class="chat-actions">
                        <button id="fahm-faris-chat-minimize" title="<?php esc_attr_e('Minimize', 'fahm-faris'); ?>">−</button>
                        <button id="fahm-faris-chat-close" title="<?php esc_attr_e('Close', 'fahm-faris'); ?>">×</button>
                    </div>
                </div>
                
                <div class="chat-messages" id="fahm-faris-chat-messages">
                    <div class="chat-message chat-message-assistant">
                        <div class="message-content">
                            <?php _e('👋 Hi! I\'m Faris, your friendly FAHM Technology Partners assistant! I\'m here to help you discover our amazing solutions and answer any questions you have. What would you like to know today?', 'fahm-faris'); ?>
                        </div>
                    </div>
                </div>
                
                <div class="chat-loading" id="fahm-faris-chat-loading">
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
                
                <div class="chat-input-container">
                    <form id="fahm-faris-chat-form">
                        <input 
                            type="text" 
                            id="fahm-faris-chat-input" 
                            class="chat-input" 
                            placeholder="<?php echo esc_attr($placeholder); ?>"
                            autocomplete="off">
                        <button type="submit" class="chat-submit" id="fahm-faris-chat-submit">
                            ➤
                        </button>
                    </form>
                </div>
            </div>
        </div>
        <?php
    }
}

// Made with Bob
