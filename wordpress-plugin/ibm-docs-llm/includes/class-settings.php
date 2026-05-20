<?php
/**
 * Settings page for IBM Docs LLM
 */

class IBM_Docs_LLM_Settings {
    
    /**
     * Initialize settings
     */
    public static function init() {
        add_action('admin_menu', array(__CLASS__, 'add_settings_page'));
        add_action('admin_init', array(__CLASS__, 'register_settings'));
    }
    
    /**
     * Add settings page to admin menu
     */
    public static function add_settings_page() {
        add_options_page(
            __('IBM Docs LLM Settings', 'ibm-docs-llm'),
            __('IBM Docs LLM', 'ibm-docs-llm'),
            'manage_options',
            'ibm-docs-llm',
            array(__CLASS__, 'render_settings_page')
        );
    }
    
    /**
     * Register settings
     */
    public static function register_settings() {
        // API Settings
        register_setting('ibm_docs_llm_settings', 'ibm_docs_llm_api_url', array(
            'type' => 'string',
            'sanitize_callback' => 'esc_url_raw',
            'default' => ''
        ));
        
        register_setting('ibm_docs_llm_settings', 'ibm_docs_llm_api_key', array(
            'type' => 'string',
            'sanitize_callback' => 'sanitize_text_field',
            'default' => ''
        ));
        
        // Widget Settings
        register_setting('ibm_docs_llm_settings', 'ibm_docs_llm_enable_widget', array(
            'type' => 'boolean',
            'default' => false
        ));
        
        register_setting('ibm_docs_llm_settings', 'ibm_docs_llm_widget_title', array(
            'type' => 'string',
            'sanitize_callback' => 'sanitize_text_field',
            'default' => __('Ask IBM Docs', 'ibm-docs-llm')
        ));
        
        register_setting('ibm_docs_llm_settings', 'ibm_docs_llm_placeholder', array(
            'type' => 'string',
            'sanitize_callback' => 'sanitize_text_field',
            'default' => __('Ask a question about IBM...', 'ibm-docs-llm')
        ));
        
        register_setting('ibm_docs_llm_settings', 'ibm_docs_llm_theme', array(
            'type' => 'string',
            'sanitize_callback' => 'sanitize_text_field',
            'default' => 'light'
        ));
        
        register_setting('ibm_docs_llm_settings', 'ibm_docs_llm_position', array(
            'type' => 'string',
            'sanitize_callback' => 'sanitize_text_field',
            'default' => 'bottom-right'
        ));
        
        // Add settings sections
        add_settings_section(
            'ibm_docs_llm_api_section',
            __('API Configuration', 'ibm-docs-llm'),
            array(__CLASS__, 'render_api_section'),
            'ibm-docs-llm'
        );
        
        add_settings_section(
            'ibm_docs_llm_widget_section',
            __('Widget Settings', 'ibm-docs-llm'),
            array(__CLASS__, 'render_widget_section'),
            'ibm-docs-llm'
        );
        
        // Add settings fields
        add_settings_field(
            'ibm_docs_llm_api_url',
            __('API URL', 'ibm-docs-llm'),
            array(__CLASS__, 'render_api_url_field'),
            'ibm-docs-llm',
            'ibm_docs_llm_api_section'
        );
        
        add_settings_field(
            'ibm_docs_llm_api_key',
            __('API Key', 'ibm-docs-llm'),
            array(__CLASS__, 'render_api_key_field'),
            'ibm-docs-llm',
            'ibm_docs_llm_api_section'
        );
        
        add_settings_field(
            'ibm_docs_llm_enable_widget',
            __('Enable Floating Widget', 'ibm-docs-llm'),
            array(__CLASS__, 'render_enable_widget_field'),
            'ibm-docs-llm',
            'ibm_docs_llm_widget_section'
        );
        
        add_settings_field(
            'ibm_docs_llm_widget_title',
            __('Widget Title', 'ibm-docs-llm'),
            array(__CLASS__, 'render_widget_title_field'),
            'ibm-docs-llm',
            'ibm_docs_llm_widget_section'
        );
        
        add_settings_field(
            'ibm_docs_llm_placeholder',
            __('Input Placeholder', 'ibm-docs-llm'),
            array(__CLASS__, 'render_placeholder_field'),
            'ibm-docs-llm',
            'ibm_docs_llm_widget_section'
        );
        
        add_settings_field(
            'ibm_docs_llm_theme',
            __('Theme', 'ibm-docs-llm'),
            array(__CLASS__, 'render_theme_field'),
            'ibm-docs-llm',
            'ibm_docs_llm_widget_section'
        );
        
        add_settings_field(
            'ibm_docs_llm_position',
            __('Widget Position', 'ibm-docs-llm'),
            array(__CLASS__, 'render_position_field'),
            'ibm-docs-llm',
            'ibm_docs_llm_widget_section'
        );
    }
    
    /**
     * Render settings page
     */
    public static function render_settings_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        
        // Handle test connection
        if (isset($_POST['test_connection'])) {
            check_admin_referer('ibm_docs_llm_test_connection');
            $api_client = new IBM_Docs_LLM_API_Client();
            $result = $api_client->test_connection();
            
            if ($result['success']) {
                add_settings_error(
                    'ibm_docs_llm_messages',
                    'ibm_docs_llm_message',
                    $result['message'],
                    'success'
                );
            } else {
                add_settings_error(
                    'ibm_docs_llm_messages',
                    'ibm_docs_llm_message',
                    $result['message'],
                    'error'
                );
            }
        }
        
        ?>
        <div class="wrap">
            <h1><?php echo esc_html(get_admin_page_title()); ?></h1>
            
            <?php settings_errors('ibm_docs_llm_messages'); ?>
            
            <form action="options.php" method="post">
                <?php
                settings_fields('ibm_docs_llm_settings');
                do_settings_sections('ibm-docs-llm');
                submit_button(__('Save Settings', 'ibm-docs-llm'));
                ?>
            </form>
            
            <form method="post" style="margin-top: 20px;">
                <?php wp_nonce_field('ibm_docs_llm_test_connection'); ?>
                <?php submit_button(__('Test API Connection', 'ibm-docs-llm'), 'secondary', 'test_connection', false); ?>
            </form>
            
            <div class="card" style="margin-top: 20px;">
                <h2><?php _e('Usage Instructions', 'ibm-docs-llm'); ?></h2>
                <h3><?php _e('Shortcode', 'ibm-docs-llm'); ?></h3>
                <p><?php _e('Add the chat widget to any page or post using:', 'ibm-docs-llm'); ?></p>
                <code>[ibm_docs_chat]</code>
                
                <h3 style="margin-top: 20px;"><?php _e('Shortcode Parameters', 'ibm-docs-llm'); ?></h3>
                <ul>
                    <li><code>title</code> - <?php _e('Widget title', 'ibm-docs-llm'); ?></li>
                    <li><code>placeholder</code> - <?php _e('Input placeholder text', 'ibm-docs-llm'); ?></li>
                    <li><code>theme</code> - <?php _e('Theme (light or dark)', 'ibm-docs-llm'); ?></li>
                </ul>
                
                <p><?php _e('Example:', 'ibm-docs-llm'); ?></p>
                <code>[ibm_docs_chat title="Ask Questions" theme="dark"]</code>
            </div>
        </div>
        <?php
    }
    
    /**
     * Render API section description
     */
    public static function render_api_section() {
        echo '<p>' . __('Configure the connection to your IBM Docs LLM backend API.', 'ibm-docs-llm') . '</p>';
    }
    
    /**
     * Render widget section description
     */
    public static function render_widget_section() {
        echo '<p>' . __('Customize the appearance and behavior of the chat widget.', 'ibm-docs-llm') . '</p>';
    }
    
    /**
     * Render API URL field
     */
    public static function render_api_url_field() {
        $value = get_option('ibm_docs_llm_api_url', '');
        ?>
        <input type="url" 
               name="ibm_docs_llm_api_url" 
               value="<?php echo esc_attr($value); ?>" 
               class="regular-text"
               placeholder="https://your-api.railway.app">
        <p class="description">
            <?php _e('The URL of your backend API (e.g., https://your-api.railway.app)', 'ibm-docs-llm'); ?>
        </p>
        <?php
    }
    
    /**
     * Render API key field
     */
    public static function render_api_key_field() {
        $value = get_option('ibm_docs_llm_api_key', '');
        ?>
        <input type="password" 
               name="ibm_docs_llm_api_key" 
               value="<?php echo esc_attr($value); ?>" 
               class="regular-text">
        <p class="description">
            <?php _e('Your API key for authentication', 'ibm-docs-llm'); ?>
        </p>
        <?php
    }
    
    /**
     * Render enable widget field
     */
    public static function render_enable_widget_field() {
        $value = get_option('ibm_docs_llm_enable_widget', false);
        ?>
        <label>
            <input type="checkbox" 
                   name="ibm_docs_llm_enable_widget" 
                   value="1" 
                   <?php checked($value, true); ?>>
            <?php _e('Show floating chat widget on all pages', 'ibm-docs-llm'); ?>
        </label>
        <?php
    }
    
    /**
     * Render widget title field
     */
    public static function render_widget_title_field() {
        $value = get_option('ibm_docs_llm_widget_title', __('Ask IBM Docs', 'ibm-docs-llm'));
        ?>
        <input type="text" 
               name="ibm_docs_llm_widget_title" 
               value="<?php echo esc_attr($value); ?>" 
               class="regular-text">
        <?php
    }
    
    /**
     * Render placeholder field
     */
    public static function render_placeholder_field() {
        $value = get_option('ibm_docs_llm_placeholder', __('Ask a question about IBM...', 'ibm-docs-llm'));
        ?>
        <input type="text" 
               name="ibm_docs_llm_placeholder" 
               value="<?php echo esc_attr($value); ?>" 
               class="regular-text">
        <?php
    }
    
    /**
     * Render theme field
     */
    public static function render_theme_field() {
        $value = get_option('ibm_docs_llm_theme', 'light');
        ?>
        <select name="ibm_docs_llm_theme">
            <option value="light" <?php selected($value, 'light'); ?>><?php _e('Light', 'ibm-docs-llm'); ?></option>
            <option value="dark" <?php selected($value, 'dark'); ?>><?php _e('Dark', 'ibm-docs-llm'); ?></option>
        </select>
        <?php
    }
    
    /**
     * Render position field
     */
    public static function render_position_field() {
        $value = get_option('ibm_docs_llm_position', 'bottom-right');
        ?>
        <select name="ibm_docs_llm_position">
            <option value="bottom-right" <?php selected($value, 'bottom-right'); ?>><?php _e('Bottom Right', 'ibm-docs-llm'); ?></option>
            <option value="bottom-left" <?php selected($value, 'bottom-left'); ?>><?php _e('Bottom Left', 'ibm-docs-llm'); ?></option>
            <option value="top-right" <?php selected($value, 'top-right'); ?>><?php _e('Top Right', 'ibm-docs-llm'); ?></option>
            <option value="top-left" <?php selected($value, 'top-left'); ?>><?php _e('Top Left', 'ibm-docs-llm'); ?></option>
        </select>
        <?php
    }
}

// Made with Bob
