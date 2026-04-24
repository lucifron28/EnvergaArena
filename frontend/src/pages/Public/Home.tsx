export default function Home() {
    return (
        <div className="flex flex-col items-center justify-center py-20 text-center space-y-6">
            <h1 className="text-5xl font-extrabold text-maroon drop-shadow-sm">MSEUF Intramurals Portal</h1>
            <p className="text-xl max-w-2xl text-charcoal/80">
                Official source for schedules, results, and medal tally. Powered by Rooney AI.
            </p>
            <div className="flex gap-4 mt-8">
                <a href="/schedules" className="btn btn-primary bg-maroon hover:bg-maroon-dark text-white border-none">View Schedules</a>
                <a href="/results" className="btn btn-outline border-maroon text-maroon hover:bg-maroon hover:text-white">Live Results</a>
            </div>
        </div>
    );
}
