<?php
/**
 * Plugin Name: IBM Docs LLM
 * Plugin URI: https://github.com/yourusername/ibm-docs-llm
 * Description: AI-powered Q&A system using IBM documentation with RAG technology
 * Version: 1.0.0
 * Requires at least: 5.8
 * Requires PHP: 7.4
 * Author: Fahm Technology Partners
 * Author URI: https://fahmtechnologypartners.com
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: ibm-docs-llm
 * Domain Path: /languages
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

// Define plugin constants
define('IBM_DOCS_LLM_VERSION', '1.0.0');
define('IBM_DOCS_LLM_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('IBM_DOCS_LLM_PLUGIN_URL', plugin_dir_url(__FILE__));
define('IBM_DOCS_LLM_PLUGIN_FILE', __FILE__);

// Include required files
require_once IBM_DOCS_LLM_PLUGIN_DIR . 'includes/class-api-client.php';
require_once IBM_DOCS_LLM_PLUGIN_DIR . 'includes/class-settings.php';
require_once IBM_DOCS_LLM_PLUGIN_DIR . 'includes/class-widget.php';
require_once IBM_DOCS_LLM_PLUGIN_DIR . 'includes/class-shortcode.php';

/**
 * Initialize the plugin
 */
function ibm_docs_llm_init() {
    // Initialize settings
    IBM_Docs_LLM_Settings::init();
    
    // Initialize widget
    IBM_Docs_LLM_Widget::init();
    
    // Initialize shortcode
    IBM_Docs_LLM_Shortcode::init();
    
    // Load text domain
    load_plugin_textdomain('ibm-docs-llm', false, dirname(plugin_basename(__FILE__)) . '/languages');
}
add_action('plugins_loaded', 'ibm_docs_llm_init');

/**
 * Enqueue frontend scripts and styles
 */
function ibm_docs_llm_enqueue_scripts() {
    // Only load if widget is enabled or shortcode is present
    if (!ibm_docs_llm_should_load_assets()) {
        return;
    }
    
    // Enqueue styles
    wp_enqueue_style(
        'ibm-docs-llm-chat',
        IBM_DOCS_LLM_PLUGIN_URL . 'public/css/chat-widget.css',
        array(),
        IBM_DOCS_LLM_VERSION
    );
    
    // Enqueue scripts
    wp_enqueue_script(
        'ibm-docs-llm-chat',
        IBM_DOCS_LLM_PLUGIN_URL . 'public/js/chat-widget.js',
        array('jquery'),
        IBM_DOCS_LLM_VERSION,
        true
    );
    
    // Localize script with settings
    wp_localize_script('ibm-docs-llm-chat', 'ibmDocsLLM', array(
        'ajaxUrl' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('ibm_docs_llm_nonce'),
        'apiUrl' => get_option('ibm_docs_llm_api_url', ''),
        'apiKey' => get_option('ibm_docs_llm_api_key', ''),
        'widgetTitle' => get_option('ibm_docs_llm_widget_title', __('Ask IBM Docs', 'ibm-docs-llm')),
        'placeholder' => get_option('ibm_docs_llm_placeholder', __('Ask a question about IBM...', 'ibm-docs-llm')),
        'theme' => get_option('ibm_docs_llm_theme', 'light'),
        'position' => get_option('ibm_docs_llm_position', 'bottom-right'),
        'strings' => array(
            'send' => __('Send', 'ibm-docs-llm'),
            'thinking' => __('Thinking...', 'ibm-docs-llm'),
            'error' => __('Sorry, there was an error processing your request.', 'ibm-docs-llm'),
            'sources' => __('Sources:', 'ibm-docs-llm'),
            'close' => __('Close', 'ibm-docs-llm'),
            'minimize' => __('Minimize', 'ibm-docs-llm')
        )
    ));
}
add_action('wp_enqueue_scripts', 'ibm_docs_llm_enqueue_scripts');

/**
 * Enqueue admin scripts and styles
 */
function ibm_docs_llm_admin_enqueue_scripts($hook) {
    // Only load on plugin settings page
    if ($hook !== 'settings_page_ibm-docs-llm') {
        return;
    }
    
    wp_enqueue_style(
        'ibm-docs-llm-admin',
        IBM_DOCS_LLM_PLUGIN_URL . 'admin/css/admin.css',
        array(),
        IBM_DOCS_LLM_VERSION
    );
    
    wp_enqueue_script(
        'ibm-docs-llm-admin',
        IBM_DOCS_LLM_PLUGIN_URL . 'admin/js/admin.js',
        array('jquery'),
        IBM_DOCS_LLM_VERSION,
        true
    );
}
add_action('admin_enqueue_scripts', 'ibm_docs_llm_admin_enqueue_scripts');

/**
 * Check if assets should be loaded
 */
function ibm_docs_llm_should_load_assets() {
    global $post;
    
    // Check if floating widget is enabled
    if (get_option('ibm_docs_llm_enable_widget', false)) {
        return true;
    }
    
    // Check if shortcode is present in content
    if (is_a($post, 'WP_Post') && has_shortcode($post->post_content, 'ibm_docs_chat')) {
        return true;
    }
    
    return false;
}

/**
 * Register REST API endpoints
 */
function ibm_docs_llm_register_rest_routes() {
    register_rest_route('ibm-llm/v1', '/chat', array(
        'methods' => 'POST',
        'callback' => 'ibm_docs_llm_handle_chat',
        'permission_callback' => '__return_true'
    ));
    
    register_rest_route('ibm-llm/v1', '/test-connection', array(
        'methods' => 'POST',
        'callback' => 'ibm_docs_llm_test_connection',
        'permission_callback' => 'ibm_docs_llm_check_admin_permission'
    ));
}
add_action('rest_api_init', 'ibm_docs_llm_register_rest_routes');

/**
 * Handle chat request
 */
function ibm_docs_llm_handle_chat($request) {
    // Verify nonce
    $nonce = $request->get_header('X-WP-Nonce');
    if (!wp_verify_nonce($nonce, 'wp_rest')) {
        return new WP_Error('invalid_nonce', __('Invalid nonce', 'ibm-docs-llm'), array('status' => 403));
    }
    
    $question = sanitize_text_field($request->get_param('question'));
    $conversation_id = sanitize_text_field($request->get_param('conversation_id'));
    
    if (empty($question)) {
        return new WP_Error('empty_question', __('Question cannot be empty', 'ibm-docs-llm'), array('status' => 400));
    }
    
    // Call backend API
    $api_client = new IBM_Docs_LLM_API_Client();
    $response = $api_client->send_chat_request($question, $conversation_id);
    
    if (is_wp_error($response)) {
        return $response;
    }
    
    return rest_ensure_response($response);
}

/**
 * Test API connection
 */
function ibm_docs_llm_test_connection($request) {
    $api_url = sanitize_text_field($request->get_param('api_url'));
    $api_key = sanitize_text_field($request->get_param('api_key'));
    
    $api_client = new IBM_Docs_LLM_API_Client($api_url, $api_key);
    $result = $api_client->test_connection();
    
    return rest_ensure_response($result);
}

/**
 * Check admin permission
 */
function ibm_docs_llm_check_admin_permission() {
    return current_user_can('manage_options');
}

/**
 * AJAX handler for chat (fallback)
 */
function ibm_docs_llm_ajax_chat() {
    check_ajax_referer('ibm_docs_llm_nonce', 'nonce');
    
    $question = sanitize_text_field($_POST['question']);
    $conversation_id = sanitize_text_field($_POST['conversation_id'] ?? '');
    
    if (empty($question)) {
        wp_send_json_error(array('message' => __('Question cannot be empty', 'ibm-docs-llm')));
    }
    
    $api_client = new IBM_Docs_LLM_API_Client();
    $response = $api_client->send_chat_request($question, $conversation_id);
    
    if (is_wp_error($response)) {
        wp_send_json_error(array('message' => $response->get_error_message()));
    }
    
    wp_send_json_success($response);
}
add_action('wp_ajax_ibm_docs_llm_chat', 'ibm_docs_llm_ajax_chat');
add_action('wp_ajax_nopriv_ibm_docs_llm_chat', 'ibm_docs_llm_ajax_chat');

/**
 * Activation hook
 */
function ibm_docs_llm_activate() {
    // Set default options
    add_option('ibm_docs_llm_widget_title', __('Ask IBM Docs', 'ibm-docs-llm'));
    add_option('ibm_docs_llm_placeholder', __('Ask a question about IBM...', 'ibm-docs-llm'));
    add_option('ibm_docs_llm_theme', 'light');
    add_option('ibm_docs_llm_position', 'bottom-right');
    add_option('ibm_docs_llm_enable_widget', false);
    
    // Flush rewrite rules
    flush_rewrite_rules();
}
register_activation_hook(__FILE__, 'ibm_docs_llm_activate');

/**
 * Deactivation hook
 */
function ibm_docs_llm_deactivate() {
    // Flush rewrite rules
    flush_rewrite_rules();
}
register_deactivation_hook(__FILE__, 'ibm_docs_llm_deactivate');

// Made with Bob
