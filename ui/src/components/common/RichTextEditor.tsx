import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Highlight from '@tiptap/extension-highlight'
import TextAlign from '@tiptap/extension-text-align'
import Underline from '@tiptap/extension-underline'
import { Color } from '@tiptap/extension-color'
import { TextStyle } from '@tiptap/extension-text-style'
import './RichTextEditor.css'

interface RichTextEditorProps {
  content: string
  onChange: (html: string) => void
  placeholder?: string
  disabled?: boolean
  minHeight?: string
}

const RichTextEditor = ({ 
  content, 
  onChange, 
  placeholder = 'Write something...', 
  disabled = false,
  minHeight = '150px'
}: RichTextEditorProps) => {
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3]
        }
      }),
      Highlight.configure({
        multicolor: true
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph']
      }),
      Underline,
      TextStyle,
      Color
    ],
    content,
    editable: !disabled,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm max-w-none focus:outline-none',
        style: `min-height: ${minHeight}; padding: 12px;`
      }
    }
  })

  if (!editor) {
    return null
  }

  return (
    <div className="rich-text-editor">
      {/* Toolbar */}
      <div className="toolbar">
        {/* Text Formatting */}
        <div className="toolbar-group">
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleBold().run()}
            className={editor.isActive('bold') ? 'is-active' : ''}
            title="Bold (Ctrl+B)"
            disabled={disabled}
          >
            <strong>B</strong>
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleItalic().run()}
            className={editor.isActive('italic') ? 'is-active' : ''}
            title="Italic (Ctrl+I)"
            disabled={disabled}
          >
            <em>I</em>
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleUnderline().run()}
            className={editor.isActive('underline') ? 'is-active' : ''}
            title="Underline (Ctrl+U)"
            disabled={disabled}
          >
            <u>U</u>
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleStrike().run()}
            className={editor.isActive('strike') ? 'is-active' : ''}
            title="Strikethrough"
            disabled={disabled}
          >
            <s>S</s>
          </button>
        </div>

        <div className="toolbar-divider"></div>

        {/* Headings */}
        <div className="toolbar-group">
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
            className={editor.isActive('heading', { level: 1 }) ? 'is-active' : ''}
            title="Heading 1"
            disabled={disabled}
          >
            H1
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
            className={editor.isActive('heading', { level: 2 }) ? 'is-active' : ''}
            title="Heading 2"
            disabled={disabled}
          >
            H2
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
            className={editor.isActive('heading', { level: 3 }) ? 'is-active' : ''}
            title="Heading 3"
            disabled={disabled}
          >
            H3
          </button>
        </div>

        <div className="toolbar-divider"></div>

        {/* Lists */}
        <div className="toolbar-group">
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleBulletList().run()}
            className={editor.isActive('bulletList') ? 'is-active' : ''}
            title="Bullet List"
            disabled={disabled}
          >
            •
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
            className={editor.isActive('orderedList') ? 'is-active' : ''}
            title="Numbered List"
            disabled={disabled}
          >
            1.
          </button>
        </div>

        <div className="toolbar-divider"></div>

        {/* Text Align */}
        <div className="toolbar-group">
          <button
            type="button"
            onClick={() => editor.chain().focus().setTextAlign('left').run()}
            className={editor.isActive({ textAlign: 'left' }) ? 'is-active' : ''}
            title="Align Left"
            disabled={disabled}
          >
            ⬅
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().setTextAlign('center').run()}
            className={editor.isActive({ textAlign: 'center' }) ? 'is-active' : ''}
            title="Align Center"
            disabled={disabled}
          >
            ↔
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().setTextAlign('right').run()}
            className={editor.isActive({ textAlign: 'right' }) ? 'is-active' : ''}
            title="Align Right"
            disabled={disabled}
          >
            ➡
          </button>
        </div>

        <div className="toolbar-divider"></div>

        {/* Highlight & Colors */}
        <div className="toolbar-group">
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleHighlight({ color: '#fef08a' }).run()}
            className={editor.isActive('highlight', { color: '#fef08a' }) ? 'is-active' : ''}
            title="Yellow Highlight"
            disabled={disabled}
            style={{ backgroundColor: '#fef08a' }}
          >
            H
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleHighlight({ color: '#bfdbfe' }).run()}
            className={editor.isActive('highlight', { color: '#bfdbfe' }) ? 'is-active' : ''}
            title="Blue Highlight"
            disabled={disabled}
            style={{ backgroundColor: '#bfdbfe' }}
          >
            H
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleHighlight({ color: '#bbf7d0' }).run()}
            className={editor.isActive('highlight', { color: '#bbf7d0' }) ? 'is-active' : ''}
            title="Green Highlight"
            disabled={disabled}
            style={{ backgroundColor: '#bbf7d0' }}
          >
            H
          </button>
        </div>

        <div className="toolbar-divider"></div>

        {/* Other */}
        <div className="toolbar-group">
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleBlockquote().run()}
            className={editor.isActive('blockquote') ? 'is-active' : ''}
            title="Quote"
            disabled={disabled}
          >
            "
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleCode().run()}
            className={editor.isActive('code') ? 'is-active' : ''}
            title="Inline Code"
            disabled={disabled}
          >
            {'<>'}
          </button>
          <button
            type="button"
            onClick={() => editor.chain().focus().toggleCodeBlock().run()}
            className={editor.isActive('codeBlock') ? 'is-active' : ''}
            title="Code Block"
            disabled={disabled}
          >
            {'{ }'}
          </button>
        </div>

        <div className="toolbar-divider"></div>

        {/* Clear Formatting */}
        <div className="toolbar-group">
          <button
            type="button"
            onClick={() => editor.chain().focus().unsetAllMarks().run()}
            title="Clear Formatting"
            disabled={disabled}
          >
            ✕
          </button>
        </div>
      </div>

      {/* Editor Content */}
      <div className="editor-content">
        <EditorContent editor={editor} />
        {!content && !editor.isFocused && (
          <div className="editor-placeholder">{placeholder}</div>
        )}
      </div>
    </div>
  )
}

export default RichTextEditor
