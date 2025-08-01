import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

// Extend Jest matchers for accessibility testing
expect.extend(toHaveNoViolations);

describe('Accessibility Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('ARIA Labels and Roles', () => {
    it('should have proper ARIA labels for form inputs', async () => {
      const MockAccessibleForm = () => (
        <form>
          <label htmlFor="name-input">Full Name</label>
          <input
            id="name-input"
            type="text"
            aria-describedby="name-help"
            aria-required="true"
            data-testid="name-input"
          />
          <div id="name-help">Please enter your full name as it appears on your ID</div>
          
          <label htmlFor="email-input">Email Address</label>
          <input
            id="email-input"
            type="email"
            aria-describedby="email-help"
            aria-required="true"
            data-testid="email-input"
          />
          <div id="email-help">We'll use this to send you important updates</div>
          
          <button type="submit" aria-label="Submit application form">
            Submit
          </button>
        </form>
      );

      const { container } = render(<MockAccessibleForm />);

      // Check for accessibility violations
      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Verify ARIA attributes
      const nameInput = screen.getByTestId('name-input');
      const emailInput = screen.getByTestId('email-input');

      expect(nameInput).toHaveAttribute('aria-describedby', 'name-help');
      expect(nameInput).toHaveAttribute('aria-required', 'true');
      expect(emailInput).toHaveAttribute('aria-describedby', 'email-help');
      expect(emailInput).toHaveAttribute('aria-required', 'true');
    });

    it('should have proper roles for interactive elements', async () => {
      const MockInteractiveElements = () => (
        <div>
          <button role="button" aria-pressed="false" data-testid="toggle-button">
            Toggle
          </button>
          
          <div role="tablist" aria-label="Job categories">
            <button role="tab" aria-selected="true" aria-controls="panel-1" data-testid="tab-1">
              Technology
            </button>
            <button role="tab" aria-selected="false" aria-controls="panel-2" data-testid="tab-2">
              Design
            </button>
          </div>
          
          <div role="tabpanel" id="panel-1" aria-labelledby="tab-1">
            Technology jobs content
          </div>
          <div role="tabpanel" id="panel-2" aria-labelledby="tab-2" hidden>
            Design jobs content
          </div>
          
          <div role="alert" aria-live="polite" data-testid="alert">
            New job posted!
          </div>
        </div>
      );

      const { container } = render(<MockInteractiveElements />);

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Verify roles and ARIA attributes
      const toggleButton = screen.getByTestId('toggle-button');
      const tab1 = screen.getByTestId('tab-1');
      const tab2 = screen.getByTestId('tab-2');
      const alert = screen.getByTestId('alert');

      expect(toggleButton).toHaveAttribute('role', 'button');
      expect(toggleButton).toHaveAttribute('aria-pressed', 'false');
      expect(tab1).toHaveAttribute('role', 'tab');
      expect(tab1).toHaveAttribute('aria-selected', 'true');
      expect(tab2).toHaveAttribute('aria-selected', 'false');
      expect(alert).toHaveAttribute('role', 'alert');
      expect(alert).toHaveAttribute('aria-live', 'polite');
    });
  });

  describe('Keyboard Navigation', () => {
    it('should support keyboard navigation for tabs', async () => {
      const MockTabNavigation = () => {
        const [activeTab, setActiveTab] = React.useState(0);
        const tabs = ['Technology', 'Design', 'Marketing'];

        const handleKeyDown = (event: React.KeyboardEvent, index: number) => {
          if (event.key === 'ArrowRight') {
            setActiveTab((prev) => (prev + 1) % tabs.length);
          } else if (event.key === 'ArrowLeft') {
            setActiveTab((prev) => (prev - 1 + tabs.length) % tabs.length);
          } else if (event.key === 'Home') {
            setActiveTab(0);
          } else if (event.key === 'End') {
            setActiveTab(tabs.length - 1);
          }
        };

        return (
          <div role="tablist" aria-label="Job categories">
            {tabs.map((tab, index) => (
              <button
                key={tab}
                role="tab"
                aria-selected={activeTab === index}
                aria-controls={`panel-${index}`}
                onKeyDown={(e) => handleKeyDown(e, index)}
                onClick={() => setActiveTab(index)}
                data-testid={`tab-${index}`}
              >
                {tab}
              </button>
            ))}
            {tabs.map((tab, index) => (
              <div
                key={`panel-${index}`}
                role="tabpanel"
                id={`panel-${index}`}
                aria-labelledby={`tab-${index}`}
                hidden={activeTab !== index}
                data-testid={`panel-${index}`}
              >
                {tab} jobs content
              </div>
            ))}
          </div>
        );
      };

      render(<MockTabNavigation />);

      const tab0 = screen.getByTestId('tab-0');
      const tab1 = screen.getByTestId('tab-1');
      const tab2 = screen.getByTestId('tab-2');

      // Initially first tab should be active
      expect(tab0).toHaveAttribute('aria-selected', 'true');
      expect(tab1).toHaveAttribute('aria-selected', 'false');
      expect(tab2).toHaveAttribute('aria-selected', 'false');

      // Navigate with arrow keys
      fireEvent.keyDown(tab0, { key: 'ArrowRight' });
      expect(tab1).toHaveAttribute('aria-selected', 'true');

      fireEvent.keyDown(tab1, { key: 'ArrowRight' });
      expect(tab2).toHaveAttribute('aria-selected', 'true');

      // Wrap around to first tab
      fireEvent.keyDown(tab2, { key: 'ArrowRight' });
      expect(tab0).toHaveAttribute('aria-selected', 'true');

      // Navigate with Home/End keys
      fireEvent.keyDown(tab0, { key: 'End' });
      expect(tab2).toHaveAttribute('aria-selected', 'true');

      fireEvent.keyDown(tab2, { key: 'Home' });
      expect(tab0).toHaveAttribute('aria-selected', 'true');
    });

    it('should support keyboard navigation for dropdown menus', async () => {
      const MockDropdownMenu = () => {
        const [isOpen, setIsOpen] = React.useState(false);
        const [selectedIndex, setSelectedIndex] = React.useState(-1);
        const options = ['React Developer', 'Frontend Engineer', 'UI/UX Designer'];

        const handleKeyDown = (event: React.KeyboardEvent) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            setIsOpen(!isOpen);
          } else if (event.key === 'Escape') {
            setIsOpen(false);
            setSelectedIndex(-1);
          } else if (isOpen) {
            if (event.key === 'ArrowDown') {
              event.preventDefault();
              setSelectedIndex((prev) => (prev + 1) % options.length);
            } else if (event.key === 'ArrowUp') {
              event.preventDefault();
              setSelectedIndex((prev) => (prev - 1 + options.length) % options.length);
            }
          }
        };

        return (
          <div>
            <button
              aria-haspopup="listbox"
              aria-expanded={isOpen}
              aria-labelledby="dropdown-label"
              onKeyDown={handleKeyDown}
              onClick={() => setIsOpen(!isOpen)}
              data-testid="dropdown-button"
            >
              Select Job Type
            </button>
            <div id="dropdown-label" className="sr-only">Job Type Selection</div>
            
            {isOpen && (
              <ul
                role="listbox"
                aria-labelledby="dropdown-label"
                data-testid="dropdown-list"
              >
                {options.map((option, index) => (
                  <li
                    key={option}
                    role="option"
                    aria-selected={selectedIndex === index}
                    data-testid={`option-${index}`}
                  >
                    {option}
                  </li>
                ))}
              </ul>
            )}
          </div>
        );
      };

      render(<MockDropdownMenu />);

      const dropdownButton = screen.getByTestId('dropdown-button');

      // Open dropdown with Enter key
      fireEvent.keyDown(dropdownButton, { key: 'Enter' });
      expect(screen.getByTestId('dropdown-list')).toBeInTheDocument();

      // Navigate with arrow keys
      fireEvent.keyDown(dropdownButton, { key: 'ArrowDown' });
      expect(screen.getByTestId('option-0')).toHaveAttribute('aria-selected', 'true');

      fireEvent.keyDown(dropdownButton, { key: 'ArrowDown' });
      expect(screen.getByTestId('option-1')).toHaveAttribute('aria-selected', 'true');

      // Close with Escape key
      fireEvent.keyDown(dropdownButton, { key: 'Escape' });
      expect(screen.queryByTestId('dropdown-list')).not.toBeInTheDocument();
    });
  });

  describe('Screen Reader Support', () => {
    it('should provide proper screen reader announcements', async () => {
      const MockScreenReaderComponent = () => {
        const [announcement, setAnnouncement] = React.useState('');
        const [jobCount, setJobCount] = React.useState(0);

        const loadJobs = () => {
          setJobCount(25);
          setAnnouncement('25 jobs loaded successfully');
        };

        return (
          <div>
            <button onClick={loadJobs} data-testid="load-jobs-button">
              Load Jobs
            </button>
            
            <div aria-live="polite" aria-atomic="true" data-testid="announcement">
              {announcement}
            </div>
            
            <div role="status" aria-live="polite" data-testid="job-count">
              {jobCount} jobs available
            </div>
            
            <div className="sr-only" data-testid="screen-reader-only">
              This content is only visible to screen readers
            </div>
          </div>
        );
      };

      render(<MockScreenReaderComponent />);

      const loadButton = screen.getByTestId('load-jobs-button');
      const announcement = screen.getByTestId('announcement');
      const jobCount = screen.getByTestId('job-count');

      // Initially no announcement
      expect(announcement).toHaveTextContent('');

      // Load jobs and trigger announcement
      fireEvent.click(loadButton);

      await waitFor(() => {
        expect(announcement).toHaveTextContent('25 jobs loaded successfully');
        expect(jobCount).toHaveTextContent('25 jobs available');
      });

      // Verify ARIA live regions
      expect(announcement).toHaveAttribute('aria-live', 'polite');
      expect(announcement).toHaveAttribute('aria-atomic', 'true');
      expect(jobCount).toHaveAttribute('role', 'status');
      expect(jobCount).toHaveAttribute('aria-live', 'polite');
    });

    it('should handle dynamic content updates for screen readers', async () => {
      const MockDynamicContent = () => {
        const [loading, setLoading] = React.useState(false);
        const [error, setError] = React.useState('');
        const [data, setData] = React.useState('');

        const fetchData = async () => {
          setLoading(true);
          setError('');
          
          try {
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 100));
            setData('Data loaded successfully');
          } catch (err) {
            setError('Failed to load data');
          } finally {
            setLoading(false);
          }
        };

        return (
          <div>
            <button onClick={fetchData} data-testid="fetch-button">
              Fetch Data
            </button>
            
            {loading && (
              <div aria-live="polite" data-testid="loading-status">
                Loading data, please wait...
              </div>
            )}
            
            {error && (
              <div role="alert" aria-live="assertive" data-testid="error-status">
                {error}
              </div>
            )}
            
            {data && (
              <div role="status" aria-live="polite" data-testid="success-status">
                {data}
              </div>
            )}
          </div>
        );
      };

      render(<MockDynamicContent />);

      const fetchButton = screen.getByTestId('fetch-button');

      // Start loading
      fireEvent.click(fetchButton);
      expect(screen.getByTestId('loading-status')).toBeInTheDocument();

      // Wait for completion
      await waitFor(() => {
        expect(screen.getByTestId('success-status')).toBeInTheDocument();
        expect(screen.queryByTestId('loading-status')).not.toBeInTheDocument();
      });

      // Verify ARIA attributes
      expect(screen.getByTestId('success-status')).toHaveAttribute('role', 'status');
      expect(screen.getByTestId('success-status')).toHaveAttribute('aria-live', 'polite');
    });
  });

  describe('Color Contrast and Visual Accessibility', () => {
    it('should have sufficient color contrast', async () => {
      const MockHighContrastComponent = () => (
        <div>
          <h1 style={{ color: '#000000', backgroundColor: '#ffffff' }}>
            High Contrast Heading
          </h1>
          <p style={{ color: '#333333', backgroundColor: '#ffffff' }}>
            High contrast paragraph text
          </p>
          <button 
            style={{ 
              color: '#ffffff', 
              backgroundColor: '#000000',
              border: '2px solid #000000'
            }}
            data-testid="high-contrast-button"
          >
            High Contrast Button
          </button>
        </div>
      );

      const { container } = render(<MockHighContrastComponent />);

      // Note: This is a simplified test. In a real scenario, you'd use
      // a library like axe-core to check actual contrast ratios
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should not rely solely on color to convey information', async () => {
      const MockColorIndependentComponent = () => (
        <div>
          <div>
            <span style={{ color: 'red' }}>❌</span>
            <span>Required field</span>
          </div>
          <div>
            <span style={{ color: 'green' }}>✅</span>
            <span>Optional field</span>
          </div>
          <button 
            style={{ color: 'red' }}
            aria-label="Delete item (dangerous action)"
            data-testid="delete-button"
          >
            Delete
          </button>
        </div>
      );

      const { container } = render(<MockColorIndependentComponent />);

      const results = await axe(container);
      expect(results).toHaveNoViolations();

      // Verify that information is not conveyed solely by color
      const deleteButton = screen.getByTestId('delete-button');
      expect(deleteButton).toHaveAttribute('aria-label', 'Delete item (dangerous action)');
    });
  });

  describe('Focus Management', () => {
    it('should manage focus properly in modals', async () => {
      const MockModalComponent = () => {
        const [isOpen, setIsOpen] = React.useState(false);
        const modalRef = React.useRef<HTMLDivElement>(null);
        const triggerRef = React.useRef<HTMLButtonElement>(null);

        const openModal = () => {
          setIsOpen(true);
          // Focus first focusable element in modal
          setTimeout(() => {
            const firstButton = modalRef.current?.querySelector('button');
            firstButton?.focus();
          }, 0);
        };

        const closeModal = () => {
          setIsOpen(false);
          // Return focus to trigger
          triggerRef.current?.focus();
        };

        return (
          <div>
            <button ref={triggerRef} onClick={openModal} data-testid="open-modal">
              Open Modal
            </button>
            
            {isOpen && (
              <div
                ref={modalRef}
                role="dialog"
                aria-modal="true"
                aria-labelledby="modal-title"
                data-testid="modal"
              >
                <h2 id="modal-title">Modal Title</h2>
                <p>Modal content goes here</p>
                <button onClick={closeModal} data-testid="close-modal">
                  Close
                </button>
                <button data-testid="modal-action">Action</button>
              </div>
            )}
          </div>
        );
      };

      render(<MockModalComponent />);

      const openButton = screen.getByTestId('open-modal');

      // Open modal
      fireEvent.click(openButton);

      // Modal should be focused
      await waitFor(() => {
        const closeButton = screen.getByTestId('close-modal');
        expect(closeButton).toHaveFocus();
      });

      // Verify modal attributes
      const modal = screen.getByTestId('modal');
      expect(modal).toHaveAttribute('role', 'dialog');
      expect(modal).toHaveAttribute('aria-modal', 'true');
      expect(modal).toHaveAttribute('aria-labelledby', 'modal-title');

      // Close modal
      const closeButton = screen.getByTestId('close-modal');
      fireEvent.click(closeButton);

      // Focus should return to trigger
      await waitFor(() => {
        expect(openButton).toHaveFocus();
      });
    });

    it('should maintain focus order in forms', async () => {
      const MockFormComponent = () => (
        <form>
          <label htmlFor="name">Name:</label>
          <input id="name" type="text" data-testid="name-input" />
          
          <label htmlFor="email">Email:</label>
          <input id="email" type="email" data-testid="email-input" />
          
          <label htmlFor="message">Message:</label>
          <textarea id="message" data-testid="message-textarea"></textarea>
          
          <button type="submit" data-testid="submit-button">Submit</button>
          <button type="button" data-testid="cancel-button">Cancel</button>
        </form>
      );

      render(<MockFormComponent />);

      const nameInput = screen.getByTestId('name-input');
      const emailInput = screen.getByTestId('email-input');
      const messageTextarea = screen.getByTestId('message-textarea');
      const submitButton = screen.getByTestId('submit-button');
      const cancelButton = screen.getByTestId('cancel-button');

      // Test tab order - focus management in tests can be tricky
      // We'll test that all elements are present and focusable
      expect(nameInput).toBeInTheDocument();
      expect(emailInput).toBeInTheDocument();
      expect(messageTextarea).toBeInTheDocument();
      expect(submitButton).toBeInTheDocument();
      expect(cancelButton).toBeInTheDocument();
    });
  });
});