import React from 'react';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import { describe, it, expect, afterEach } from 'vitest';
import ROISimulator from './ROISimulator';

afterEach(() => {
  cleanup();
});

describe('ROISimulator', () => {
  it('renders correctly with default volume 50', () => {
    render(<ROISimulator />);
    
    // Default margin = 50 * (1500 - 90) = 50 * 1410 = 70500
    // format is "70 500 €" or "70 500 €" in fr-FR, so regex is better
    expect(screen.getByText(/70\s*500/)).toBeDefined();
    
    // Default hourly rate = 70500 / (0.5 * 50) = 70500 / 25 = 2820
    expect(screen.getByText(/2\s*820/)).toBeDefined();
  });

  it('updates calculations when volume changes', () => {
    render(<ROISimulator />);
    const numberInputs = screen.getAllByDisplayValue('50');
    
    // Change volume to 10 using the number input (the second one)
    fireEvent.change(numberInputs[1], { target: { value: '10' } });
    
    // Margin = 10 * 1410 = 14100
    expect(screen.getByText(/14\s*100/)).toBeDefined();
    
    // Hourly rate = 14100 / (0.5 * 10) = 14100 / 5 = 2820
    expect(screen.getByText(/2\s*820/)).toBeDefined();
  });
});
