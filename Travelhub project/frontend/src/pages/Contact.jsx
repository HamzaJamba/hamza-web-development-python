export default function Contact() {
  return (
    <div className="max-w-xl mx-auto px-4 py-20">
      <h1 className="text-3xl font-bold mb-4 text-center">Contact Us</h1>
      <form className="space-y-4 mt-8">
        <input placeholder="Your name" className="w-full px-4 py-2.5 rounded-xl border border-black/10 dark:border-white/15 bg-white dark:bg-[#0f2422] text-sm outline-none" />
        <input placeholder="Email" className="w-full px-4 py-2.5 rounded-xl border border-black/10 dark:border-white/15 bg-white dark:bg-[#0f2422] text-sm outline-none" />
        <textarea placeholder="Message" rows={4} className="w-full px-4 py-2.5 rounded-xl border border-black/10 dark:border-white/15 bg-white dark:bg-[#0f2422] text-sm outline-none" />
        <button type="submit" className="w-full bg-[var(--color-primary)] text-white font-medium py-2.5 rounded-xl">Send Message</button>
      </form>
    </div>
  )
}
