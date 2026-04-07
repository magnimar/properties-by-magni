import { chromium } from 'playwright';

(async () => {
  const htmlContent = `
  <!DOCTYPE html>
  <html>
  <head>
    <style>
      body { font-family: sans-serif; padding: 40px; color: #333; }
      h1, h2 { color: #111; }
      .screenshot { border: 1px solid #ccc; padding: 20px; border-radius: 8px; margin-bottom: 40px; background: #fafafa; }
      .banner { background: #fefce8; border-left: 4px solid #facc15; padding: 16px; display: flex; justify-content: space-between; align-items: center; border-radius: 4px; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); }
      .banner-text { display: flex; align-items: center; gap: 12px; }
      .banner-text p { color: #a16207; font-size: 14px; margin: 0; font-weight: 500; }
      .btn-upgrade { background: #eab308; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; font-size: 14px; cursor: pointer; }
      
      .pricing-table { display: flex; gap: 24px; margin-top: 20px; }
      .plan { flex: 1; border: 1px solid #e5e7eb; padding: 24px; border-radius: 8px; background: white; text-align: center; }
      .plan.pro { border-color: #3b82f6; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
      .plan-title { font-size: 20px; font-weight: bold; margin-bottom: 16px; }
      .plan-price { font-size: 36px; font-weight: bold; margin-bottom: 8px; }
      .plan-price span { font-size: 16px; font-weight: normal; color: #6b7280; }
      .plan-features { list-style: none; padding: 0; margin-bottom: 24px; text-align: left; }
      .plan-features li { margin-bottom: 8px; font-size: 14px; color: #4b5563; }
      .btn-select { background: #3b82f6; color: white; border: none; padding: 12px 24px; border-radius: 4px; font-weight: bold; font-size: 16px; cursor: pointer; width: 100%; }
      
      .checkout-section { background: white; border: 1px solid #e5e7eb; padding: 24px; border-radius: 8px; margin-top: 20px; }
      .checkbox-container { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 20px; }
      .checkbox-container input { margin-top: 4px; }
      .checkbox-text { font-size: 14px; color: #4b5563; line-height: 1.5; }
      .checkbox-text a { color: #3b82f6; text-decoration: none; }
    </style>
  </head>
  <body>
    <h1>Fundvís Sign-Up & Upgrade Flow Mockups</h1>
    <p>These mockups demonstrate the user journey for upgrading to a Pro subscription, including the compliance requirements.</p>
    
    <h2>1. Dashboard Non-Pro Banner</h2>
    <p>When a user is on a free/trial account, they see this banner at the top of their dashboard.</p>
    <div class="screenshot">
      <div class="banner">
        <div class="banner-text">
          <svg style="width: 20px; height: 20px; color: #facc15;" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <p>Þú ert á prufureikning, til þess að hafa fullt aðgengi að öllum eiginleikum síðunnar verður þú að kaupa áskrift.</p>
        </div>
        <button class="btn-upgrade">Kaupa áskrift</button>
      </div>
    </div>

    <h2>2. Pricing Table (Upgrade Modal)</h2>
    <p>Clicking "Kaupa áskrift" presents the user with the pricing options, clearly stating the monthly cost.</p>
    <div class="screenshot">
      <div class="pricing-table">
        <div class="plan pro">
          <div class="plan-title">Fundvís Pro</div>
          <div class="plan-price">999 ISK<span> / month</span></div>
          <ul class="plan-features">
            <li>✓ Full access to all property data</li>
            <li>✓ Unlimited property watches</li>
            <li>✓ Instant email notifications</li>
            <li>✓ Auto-renews monthly unless cancelled</li>
          </ul>
          <button class="btn-select">Select Pro</button>
        </div>
      </div>
    </div>

    <h2>3. Checkout & Terms Agreement</h2>
    <p>Before completing the payment, the user must explicitly agree to the Terms of Service and acknowledge the recurring subscription.</p>
    <div class="screenshot">
      <div class="checkout-section">
        <h3>Order Summary</h3>
        <p style="font-weight: bold; font-size: 18px; margin-bottom: 24px;">Total: 999 ISK</p>
        
        <div class="checkbox-container">
          <input type="checkbox" id="terms" checked>
          <div class="checkbox-text">
            <label for="terms">
              I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>. 
              <br><br>
              I understand that I am subscribing to Fundvís Pro for <strong>999 ISK per month</strong>, and that my subscription will automatically renew each month until cancelled. I can cancel at any time from my account settings.
            </label>
          </div>
        </div>
        
        <button class="btn-select" style="background: #22c55e;">Pay 999 ISK & Subscribe</button>
      </div>
    </div>

  </body>
  </html>
  `;

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent(htmlContent);
  await page.pdf({ path: '../compliance/signup_flow_mockups.pdf', format: 'A4' });
  await browser.close();
})();
