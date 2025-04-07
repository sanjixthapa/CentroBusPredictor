import '../css/Help.css'

function Help(){
    return (
        <div class="help-container">
        <h1>Help Center - Centro Bus Predictor</h1>
        <p>Welcome to the help page! Here’s how to use the Centro Bus Predictor.</p>

        
        <h2>Getting Started</h2>
        <ul>
            <li><strong>Search for a Bus Route:</strong> Enter your route number or destination and press search.</li>
            <li><strong>View Live Bus Arrivals:</strong> Select a route and stop to see real-time updates.</li>
            <li><strong>Save Favorite Routes:</strong> Click “Add to Favorites” for quick access.</li>
            <li><strong>Delay Notifications:</strong> See alerts about bus delays and estimated wait times.</li>
        </ul>

        
        <h2>Frequently Asked Questions (FAQ)</h2>
        <p><strong>How accurate are the bus times?</strong> They are based on real-time tracking but may vary due to traffic and weather.</p>
        <p><strong>Why is my bus route not showing?</strong> Double-check the route number, or it may not be available at that time.</p>
        <p><strong>Can I use this app on my phone?</strong> Yes! It works on all modern mobile browsers.</p>

        
        <h2>Troubleshooting</h2>
        <table>
            <tr>
                <th>Error Message</th>
                <th>Possible Cause</th>
                <th>Solution</th>
            
            </tr>
            <tr>
                <td>No Bus Data Available</td>
                <td>Centro API may be down</td>
                <td>Try again later</td>
            </tr>
            <tr>
                <td>Invalid Route Number</td>
                <td>Mistyped or nonexistent route</td>
                <td>Double-check the route number</td>
            </tr>
            <tr>
                <td>Weather Data Not Loading</td>
                <td>Weather API issue</td>
                <td>Retry in a few minutes</td>
            </tr>
        </table>

        
        <div class="contact-info">
            <h2>Contact Support</h2>
            <p>Email: <a href="mailto:support@centrobuspredictor.com">support@centrobuspredictor.com</a></p>
            <p>Phone: (315) 442-3400</p>
            <p>Live Chat: Available from 9 AM - 5 PM EST</p>
        </div>
    </div>
    )
}

export default Help;