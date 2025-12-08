"""51CTO Crawler Service - Playwright Version"""
from playwright.sync_api import sync_playwright, Page, Browser
import time
import random
import hashlib
import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Callable

logger = logging.getLogger(__name__)


class CTO51Crawler:
    """51CTO Article Crawler using Playwright"""
    
    def __init__(self, min_article_id: int = 33500, data_file: str = "data/51cto_articles.json"):
        self.base_url = "https://ost.51cto.com/postlist"
        self.source = "51CTO"
        self.category = "技术文章"
        self.min_article_id = min_article_id
        self.data_file = data_file
        self.scraped_urls = set()
        self.playwright = None
        self.browser = None
        self.page = None
        
        # Load existing data
        self._load_existing_data()
    
    def _load_existing_data(self):
        """Load existing crawled data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    existing_articles = json.load(f)
                    self.scraped_urls = {article['url'] for article in existing_articles if article.get('url')}
                    logger.info(f"✅ Loaded {len(existing_articles)} existing articles from {self.data_file}")
                    logger.info(f"📋 {len(self.scraped_urls)} URLs in history")
            else:
                logger.info(f"📝 No existing data file found, will create new one")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load existing data: {e}")
            self.scraped_urls = set()
    
    def _save_data(self, articles: List[Dict]):
        """Save articles to file"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Load existing data
            existing_articles = []
            if os.path.exists(self.data_file):
                try:
                    with open(self.data_file, 'r', encoding='utf-8') as f:
                        existing_articles = json.load(f)
                except:
                    pass
            
            # Merge with new articles (avoid duplicates)
            existing_urls = {article['url'] for article in existing_articles if article.get('url')}
            new_articles = [article for article in articles if article['url'] not in existing_urls]
            
            if new_articles:
                all_articles = existing_articles + new_articles
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(all_articles, f, ensure_ascii=False, indent=2)
                logger.info(f"💾 Saved {len(new_articles)} new articles to {self.data_file}")
                logger.info(f"📊 Total articles in file: {len(all_articles)}")
            else:
                logger.info(f"📝 No new articles to save")
                
        except Exception as e:
            logger.error(f"❌ Failed to save data: {e}")
    
    def setup_browser(self):
        """Setup Playwright browser"""
        logger.info("Starting Chromium browser with UI...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,  # 显示浏览器窗口
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        # Create context with anti-detection
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        )
        
        # Add anti-detection script
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = context.new_page()
        logger.info("✅ Chromium browser started successfully (with UI)")
    
    def _random_delay(self, min_sec: float = 2, max_sec: float = 5):
        """Random delay"""
        time.sleep(random.uniform(min_sec, max_sec))
    
    def _human_like_scroll(self):
        """Human-like scrolling"""
        try:
            total_height = self.page.evaluate("document.body.scrollHeight")
            current_position = 0
            max_scrolls = 10
            scroll_count = 0
            
            while current_position < total_height and scroll_count < max_scrolls:
                scroll_distance = random.randint(300, 600)
                current_position += scroll_distance
                self.page.evaluate(f"window.scrollTo(0, {current_position})")
                time.sleep(random.uniform(0.3, 0.8))
                scroll_count += 1
                
                new_height = self.page.evaluate("document.body.scrollHeight")
                if new_height > total_height:
                    total_height = new_height
        except Exception as e:
            logger.warning(f"Scroll error: {e}")
    
    def _extract_content(self) -> List[Dict]:
        """Extract article content"""
        try:
            content_container = self.page.query_selector(".posts-content")
            if not content_container:
                logger.warning("Content container not found")
                return []
        except:
            logger.warning("Content container not found")
            return []
        
        js_script = r"""
(element) => {
    let blocks = [];
    let processedNodes = new Set();
    
    function getCodeLanguage(node) {
        const classNames = node.className || '';
        const langMatch = classNames.match(/(?:language-|lang-|brush:)?(python|javascript|java|cpp|c\+\+|csharp|c#|php|ruby|go|rust|swift|kotlin|typescript|sql|bash|shell|html|css|json|xml|yaml)/i);
        if (langMatch) {
            return langMatch[1].toLowerCase();
        }
        
        if (node.nodeName === 'PRE') {
            const codeElem = node.querySelector('code');
            if (codeElem) {
                const codeClass = codeElem.className || '';
                const codeLangMatch = codeClass.match(/(?:language-|lang-|brush:)?(python|javascript|java|cpp|c\+\+|csharp|c#|php|ruby|go|rust|swift|kotlin|typescript|sql|bash|shell|html|css|json|xml|yaml)/i);
                if (codeLangMatch) {
                    return codeLangMatch[1].toLowerCase();
                }
            }
        }
        
        return '';
    }
    
    function getCodeText(node) {
        const clone = node.cloneNode(true);
        const lineNumbers = clone.querySelectorAll('.pre-numbering, .line-numbers, .line-number, ul.pre-numbering');
        lineNumbers.forEach(elem => elem.remove());
        return clone.textContent.trim();
    }
    
    function processNode(node) {
        if (['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(node.nodeName)) return;
        if (processedNodes.has(node)) return;
        
        if (node.nodeType === Node.ELEMENT_NODE) {
            const tagName = node.nodeName;
            
            if (tagName === 'IMG') {
                const src = node.src || node.getAttribute('data-src') || node.getAttribute('data-original') || '';
                if (src && src.startsWith('http')) {
                    blocks.push({type: 'image', value: src});
                }
                return;
            }
            
            if (tagName === 'PRE') {
                processedNodes.add(node);
                const codeText = getCodeText(node);
                if (codeText) {
                    const language = getCodeLanguage(node);
                    blocks.push({
                        type: 'code',
                        value: codeText,
                        language: language
                    });
                }
                return;
            }
            
            if (tagName === 'CODE') {
                const parent = node.parentElement;
                if (parent && parent.nodeName === 'PRE') {
                    return;
                }
                processedNodes.add(node);
                const codeText = getCodeText(node);
                if (codeText) {
                    const language = getCodeLanguage(node);
                    blocks.push({
                        type: 'code',
                        value: codeText,
                        language: language
                    });
                }
                return;
            }
            
            if (['P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6'].includes(tagName)) {
                const images = node.querySelectorAll('img');
                const codeBlocks = node.querySelectorAll('pre, code');
                
                if (images.length > 0 || codeBlocks.length > 0) {
                    for (let child of node.childNodes) {
                        processNode(child);
                    }
                    return;
                }
                
                let text = node.textContent.trim();
                if (text && text.length > 10 && !text.match(/^[\w\-]+\.(png|jpg|jpeg|gif|svg|webp)$/i)) {
                    blocks.push({type: 'text', value: text});
                }
                return;
            }
            
            if (tagName === 'DIV') {
                const codeBlocks = node.querySelectorAll('pre, code');
                if (codeBlocks.length > 0) {
                    for (let child of node.childNodes) {
                        processNode(child);
                    }
                    return;
                }
                
                const images = node.querySelectorAll('img');
                if (images.length > 0) {
                    for (let child of node.childNodes) {
                        processNode(child);
                    }
                    return;
                }
                
                for (let child of node.childNodes) {
                    processNode(child);
                }
                return;
            }
            
            for (let child of node.childNodes) {
                processNode(child);
            }
        }
        
        if (node.nodeType === Node.TEXT_NODE) {
            let text = node.textContent.trim();
            if (text && text.length > 10 && !text.match(/^[\w\-]+\.(png|jpg|jpeg|gif|svg|webp)$/i)) {
                blocks.push({type: 'text', value: text});
            }
        }
    }
    
    processNode(element);
    return blocks;
}
"""
        try:
            content_blocks = content_container.evaluate(js_script)
            valid_blocks = []
            for block in content_blocks:
                if isinstance(block, dict) and 'type' in block and 'value' in block:
                    if block['type'] in ['text', 'image', 'code']:
                        valid_blocks.append(block)
            return valid_blocks if valid_blocks else []
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            try:
                text = content_container.text_content().strip()
                if text:
                    return [{"type": "text", "value": text}]
            except:
                pass
            return []
    
    def _standardize_date(self, date_str: str) -> str:
        """Standardize date format to YYYY-MM-DD"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        try:
            import re
            patterns = [
                r'(\d{4})[.\-\/年](\d{1,2})[.\-\/月](\d{1,2})',
                r'(\d{1,2})[.\-\/](\d{1,2})[.\-\/](\d{4})',
            ]
            for pattern in patterns:
                match = re.search(pattern, str(date_str))
                if match:
                    groups = match.groups()
                    if len(groups) == 3:
                        if int(groups[0]) > 1900:
                            year, month, day = groups
                        else:
                            day, month, year = groups
                        return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
            logger.warning(f"Cannot parse date: {date_str}, using current date")
            return datetime.now().strftime('%Y-%m-%d')
        except Exception as e:
            logger.error(f"Date standardization failed: {e}")
            return datetime.now().strftime('%Y-%m-%d')
    
    def _format_article(self, article_data: Dict) -> Dict:
        """Format article to HongYiXun format"""
        article_id = hashlib.md5(article_data['url'].encode()).hexdigest()[:16]
        standardized_date = self._standardize_date(article_data.get('publish_time', ''))
        
        summary = ""
        if article_data.get('content'):
            for block in article_data['content']:
                if block.get('type') == 'text':
                    text = block.get('value', '')
                    if text:
                        summary = text[:200] + ('...' if len(text) > 200 else '')
                        break
        
        return {
            "id": article_id,
            "title": article_data['title'],
            "date": standardized_date,
            "url": article_data['url'],
            "content": article_data.get('content', []),
            "category": self.category,
            "summary": summary,
            "source": self.source,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def _get_article_list(self) -> Dict:
        """Get article list from current page"""
        article_elements = []
        old_articles_count = 0
        total_valid_articles = 0
        
        try:
            self.page.wait_for_selector("ul.infinite-list", timeout=10000)
            self._human_like_scroll()
            list_items = self.page.query_selector_all("ul.infinite-list > li")
            logger.info(f"Found {len(list_items)} article items")
            
            for idx, item in enumerate(list_items, 1):
                try:
                    link_elem = item.query_selector("a[href*='posts']")
                    if not link_elem:
                        continue
                    
                    url = link_elem.get_attribute('href')
                    
                    article_id = None
                    try:
                        article_id = int(url.split('/posts/')[-1])
                    except:
                        pass
                    
                    try:
                        title_elem = item.query_selector("h3.title-h3")
                        title = title_elem.text_content().strip() if title_elem else ""
                    except:
                        title = link_elem.text_content().strip().split('\n')[0]
                    
                    if not title:
                        title = "无标题"
                    
                    if article_id and article_id <= self.min_article_id:
                        logger.info(f"Skip old article: {title} (ID: {article_id})")
                        old_articles_count += 1
                        continue
                    
                    total_valid_articles += 1
                    
                    # Check if already crawled
                    if url in self.scraped_urls:
                        logger.info(f"[{idx}] ⏭️  Skip crawled: {title} (ID: {article_id})")
                        continue
                    
                    article_elements.append({
                        'url': url,
                        'title': title,
                        'article_id': article_id
                    })
                    logger.info(f"[{idx}] 📄 To crawl: {title} (ID: {article_id})")
                except Exception as e:
                    logger.warning(f"[{idx}] Parse failed: {e}")
                    continue
            
            logger.info(f"Got {len(article_elements)} new articles to crawl")
            return {
                'articles': article_elements,
                'all_old': (total_valid_articles == 0 and old_articles_count > 0)
            }
        except Exception as e:
            logger.error(f"Get article list failed: {e}")
            return {'articles': [], 'all_old': False}
    
    def _crawl_single_article(self, article_info: Dict) -> Optional[Dict]:
        """Crawl single article"""
        url = article_info['url']
        title = article_info['title']
        
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.warning(f"Retry attempt {attempt + 1}/{max_retries} for: {title}")
                
                article_data = {
                    'title': title,
                    'url': url,
                    'author': None,
                    'publish_time': None,
                    'content': []
                }
                
                logger.info(f"Opening article: {title}")
                
                # Open in new page
                new_page = self.page.context.new_page()
                new_page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait for content
                try:
                    new_page.wait_for_selector(".posts-content", timeout=20000)
                    logger.info("✅ Article content loaded successfully")
                except:
                    logger.warning(f"⚠️ Content not loaded within 20 seconds")
                    new_page.close()
                    if attempt < max_retries - 1:
                        self._random_delay(2, 3)
                        continue
                    else:
                        return None
                
                # Scroll
                new_page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self._random_delay(1, 2)
                
                # Extract author
                try:
                    for selector in [".name", ".author", ".post-author"]:
                        try:
                            author_elem = new_page.query_selector(selector)
                            if author_elem:
                                article_data['author'] = author_elem.text_content().strip()
                                if article_data['author']:
                                    break
                        except:
                            continue
                except:
                    pass
                
                # Extract publish time
                try:
                    for selector in ["time", ".publish-time", ".post-time"]:
                        try:
                            time_elem = new_page.query_selector(selector)
                            if time_elem:
                                article_data['publish_time'] = time_elem.text_content().strip()
                                if article_data['publish_time']:
                                    break
                        except:
                            continue
                except:
                    pass
                
                # Extract content
                logger.info("Extracting article content...")
                content_container = new_page.query_selector(".posts-content")
                if content_container:
                    article_data['content'] = self._extract_content()
                
                # Verify content
                if not article_data['content'] or len(article_data['content']) == 0:
                    logger.warning(f"⚠️ Extracted content is empty")
                    new_page.close()
                    if attempt < max_retries - 1:
                        self._random_delay(2, 3)
                        continue
                    else:
                        return None
                
                logger.info(f"✅ Successfully crawled article!")
                logger.info(f"  - Author: {article_data['author'] or 'Unknown'}")
                logger.info(f"  - Publish time: {article_data['publish_time'] or 'Unknown'}")
                logger.info(f"  - Content blocks: {len(article_data['content'])}")
                
                formatted_article = self._format_article(article_data)
                
                new_page.close()
                self._random_delay(1, 2)
                
                return formatted_article
                
            except Exception as e:
                logger.error(f"Crawl attempt {attempt + 1} failed: {title}")
                logger.error(f"  Error: {e}")
                
                if attempt < max_retries - 1:
                    self._random_delay(2, 3)
                    continue
                else:
                    return None
        
        return None
    
    def _click_next_page(self) -> bool:
        """Click next page button"""
        try:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self._random_delay(1, 2)
            
            next_button = self.page.query_selector("a:has-text('下一页'), button:has-text('下一页')")
            
            if next_button:
                next_button.scroll_into_view_if_needed()
                self._random_delay(0.5, 1)
                next_button.click()
                logger.info("Clicked next page")
                self._random_delay(3, 5)
                return True
            else:
                logger.info("Next page button not found")
                return False
        except Exception as e:
            logger.error(f"Click next page failed: {e}")
            return False
    
    def crawl_all_pages(self,
                       max_pages: Optional[int] = None,
                       batch_callback: Optional[Callable[[List[Dict]], None]] = None,
                       batch_size: int = 5) -> List[Dict]:
        """Crawl all pages"""
        all_articles = []
        batch_articles = []
        
        try:
            self.setup_browser()
            logger.info(f"Visiting list page: {self.base_url}")
            self.page.goto(self.base_url, wait_until='domcontentloaded')
            logger.info("List page loaded")
            self._random_delay(3, 6)
            
            page_count = 1
            old_pages = 0
            max_old_pages = 3
            
            while True:
                logger.info(f"\n{'='*60}")
                logger.info(f"Crawling page {page_count}")
                logger.info(f"{'='*60}")
                
                result = self._get_article_list()
                article_elements = result['articles']
                all_old = result['all_old']
                
                if all_old:
                    old_pages += 1
                    logger.warning(f"All old articles on this page ({old_pages}/{max_old_pages})")
                    if old_pages >= max_old_pages:
                        logger.info(f"Stop: {max_old_pages} consecutive pages with old articles")
                        break
                else:
                    old_pages = 0
                
                if len(article_elements) == 0:
                    logger.info("No new articles on this page, continue to next page...")
                else:
                    logger.info(f"Start crawling {len(article_elements)} articles\n")
                    
                    for i, article_info in enumerate(article_elements, 1):
                        logger.info(f"{'─'*60}")
                        logger.info(f"[{i}/{len(article_elements)}] {article_info['title']}")
                        logger.info(f"{'─'*60}")
                        
                        article = self._crawl_single_article(article_info)
                        
                        if article:
                            all_articles.append(article)
                            batch_articles.append(article)
                            
                            # Mark as crawled
                            self.scraped_urls.add(article['url'])
                            
                            if len(batch_articles) >= batch_size:
                                if batch_callback:
                                    try:
                                        logger.info(f"[Batch] Processing {len(batch_articles)} articles")
                                        batch_callback(batch_articles.copy())
                                        logger.info("[Batch] Callback executed successfully")
                                    except Exception as e:
                                        logger.error(f"[Batch] Callback failed: {e}")
                                
                                # Save to file
                                self._save_data(batch_articles.copy())
                                batch_articles.clear()
                        
                        if i < len(article_elements):
                            wait_time = random.uniform(2, 5)
                            logger.info(f"Waiting {wait_time:.1f} seconds...")
                            time.sleep(wait_time)
                    
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Page {page_count} completed! Crawled {len(article_elements)} new articles")
                    logger.info(f"{'='*60}")
                
                if max_pages and page_count >= max_pages:
                    logger.warning(f"⚠️ Reached max pages limit: {max_pages}")
                    break
                
                logger.info(f"\nPreparing to go to next page...")
                wait_time = random.uniform(3, 6)
                logger.info(f"Waiting {wait_time:.1f} seconds before turning page...")
                time.sleep(wait_time)
                
                if not self._click_next_page():
                    logger.info("No more pages")
                    break
                
                page_count += 1
            
            # Process remaining batch
            if batch_articles:
                if batch_callback:
                    try:
                        logger.info(f"[Batch] Processing remaining {len(batch_articles)} articles")
                        batch_callback(batch_articles.copy())
                        logger.info("[Batch] Last batch processed successfully")
                    except Exception as e:
                        logger.error(f"[Batch] Last batch failed: {e}")
                
                # Save remaining articles to file
                self._save_data(batch_articles.copy())
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Crawling completed!")
            logger.info(f"Total crawled: {len(all_articles)} articles")
            logger.info(f"{'='*60}")
            
            return all_articles
            
        except KeyboardInterrupt:
            logger.warning(f"\n⚠️ Crawling interrupted by user!")
            logger.info(f"💾 Saving {len(batch_articles)} articles before exit...")
            
            # Save remaining articles
            if batch_articles:
                try:
                    if batch_callback:
                        batch_callback(batch_articles.copy())
                    self._save_data(batch_articles.copy())
                    logger.info(f"✅ Successfully saved {len(batch_articles)} articles")
                except Exception as save_error:
                    logger.error(f"❌ Failed to save articles: {save_error}")
            
            logger.info(f"📊 Total crawled before interrupt: {len(all_articles)} articles")
            return all_articles
            
        except Exception as e:
            logger.error(f"❌ Crawling error: {e}")
            import traceback
            traceback.print_exc()
            
            # Try to save remaining articles even on error
            if batch_articles:
                logger.info(f"💾 Attempting to save {len(batch_articles)} articles after error...")
                try:
                    if batch_callback:
                        batch_callback(batch_articles.copy())
                    self._save_data(batch_articles.copy())
                    logger.info(f"✅ Successfully saved {len(batch_articles)} articles")
                except Exception as save_error:
                    logger.error(f"❌ Failed to save articles: {save_error}")
            
            return all_articles
            
        finally:
            # Close browser
            if self.browser:
                try:
                    self.browser.close()
                    logger.info("Browser closed")
                except:
                    pass
            
            if self.playwright:
                try:
                    self.playwright.stop()
                    logger.info("Playwright stopped")
                except:
                    pass
            
            # Log final statistics
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 Final Statistics:")
            logger.info(f"  - Total articles crawled this session: {len(all_articles)}")
            logger.info(f"  - Total URLs in history: {len(self.scraped_urls)}")
            logger.info(f"  - Data file: {self.data_file}")
            logger.info(f"{'='*60}")
