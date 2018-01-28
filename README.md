# The Doug Note Editor

It's time for a proper tool to make notes.

Both pencil & paper and editing text on a computer are unreasonnibly effective. 
Doug combines both.

Vision:
- Build for laptops with input pens and touch screens.
- Freeform doodling / mindmapping is the best way to support creative thinking
- Don't throw away ideas, but extend or rewrite.
- Interlinking with hyperlinks and transclusion.
  - Embedding a page, rectangle or even a paragraph of text from a PDF, with
    preservation of the context where the embedding came from.

Tech PLAN:
- [x] Create Page widget (for now don't care about scrolling/zooming)
- [x] Draw grid on page Widget 
- [x] Implement modes
  - [x] initial simple popup context menu to switch
  - [x] update mode
  - [x] send "leave-mode" and "enter-mode" events via GObject events
- [x] Draw strokes
- [x] Delete strokes
- [ ] Add gesture detection with meta button to switch between modes.
- [ ] Implement zooming & panning
- [ ] Persist a single page + invoke doug on a file name
- [ ] Make a view widget that takes a ViewConfig & a Page

TECH Later:
- [ ] improve quality of strokes by using catmulromspline to interpolate points
- [ ] decouple gathering events from drawing & deletion of strokes.
