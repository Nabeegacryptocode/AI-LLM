=== IBM Docs LLM ===
Contributors: yourusername
Tags: ai, chatbot, llm, ibm, documentation, rag
Requires at least: 6.0
Tested up to: 6.4
Requires PHP: 8.0
Stable tag: 1.0.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html

AI-powered Q&A system using IBM documentation with RAG (Retrieval Augmented Generation) technology.

== Description ==

IBM Docs LLM is a powerful WordPress plugin that brings AI-powered question answering to your website using IBM documentation as its knowledge base. The plugin uses advanced RAG (Retrieval Augmented Generation) technology to provide accurate, context-aware answers with source citations.

= Features =

* **AI-Powered Answers**: Get intelligent responses powered by GPT-4
* **Source Citations**: Every answer includes references to IBM documentation
* **Floating Chat Widget**: Add a floating chat widget to any page
* **Shortcode Support**: Embed chat interface anywhere with `[ibm_docs_chat]`
* **Customizable**: Choose themes, colors, and positioning
* **Fast & Accurate**: Semantic search with vector embeddings
* **Conversation History**: Maintains context across multiple questions
* **Responsive Design**: Works perfectly on mobile and desktop

= How It Works =

1. User asks a question
2. System searches IBM documentation using semantic search
3. Retrieves most relevant content
4. GPT-4 generates comprehensive answer with context
5. Returns answer with source citations

= Requirements =

* WordPress 6.0 or higher
* PHP 8.0 or higher
* Backend API (FastAPI) deployed and configured
* OpenAI API key
* Pinecone vector database

== Installation ==

1. Upload the plugin files to `/wp-content/plugins/ibm-docs-llm/`
2. Activate the plugin through the 'Plugins' menu in WordPress
3. Go to Settings → IBM Docs LLM
4. Configure your API URL and API Key
5. Customize widget settings
6. Use shortcode `[ibm_docs_chat]` or enable floating widget

== Frequently Asked Questions ==

= Do I need a backend API? =

Yes, this plugin requires a backend API to be deployed. See the documentation for setup instructions.

= What is RAG? =

RAG (Retrieval Augmented Generation) is a technique that combines information retrieval with AI text generation to provide accurate, grounded answers.

= Can I customize the appearance? =

Yes! You can choose between light and dark themes, customize colors, and position the widget anywhere on your site.

= Is it mobile-friendly? =

Absolutely! The chat widget is fully responsive and works great on all devices.

= How much does it cost to run? =

Costs depend on usage. Expect $26-61/month for 1000 queries (OpenAI API + hosting).

== Screenshots ==

1. Chat widget in action
2. Admin settings page
3. Shortcode usage example
4. Mobile responsive design

== Changelog ==

= 1.0.0 =
* Initial release
* Floating chat widget
* Shortcode support
* Admin settings page
* Light and dark themes
* Source citations
* Conversation history

== Upgrade Notice ==

= 1.0.0 =
Initial release of IBM Docs LLM plugin.

== Usage ==

= Shortcode =

Basic usage:
`[ibm_docs_chat]`

With parameters:
`[ibm_docs_chat title="Ask Questions" theme="dark" height="600px"]`

= Floating Widget =

Enable the floating widget in Settings → IBM Docs LLM → Enable Floating Widget

= PHP Template =

`<?php echo do_shortcode('[ibm_docs_chat]'); ?>`

== Support ==

For support, please visit the plugin documentation or contact support@example.com

== Privacy ==

This plugin sends user questions to your configured backend API. No personal data is stored by the plugin itself. Please review your backend API's privacy policy.