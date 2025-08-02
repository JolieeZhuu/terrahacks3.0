import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

export default function FlexibleBox() {
  return (
    <ResizablePanelGroup
      direction="horizontal"
      className="max-w-md rounded-lg border md:min-w-[450px]"
    >
      {/* Section One - Basic Info */}
      <ResizablePanel defaultSize={50}>
        <div className="flex flex-col gap-4 h-full justify-center p-6">
          <h2 className="text-lg font-semibold">Basic Information</h2>

          <div className="flex flex-col gap-2">
            <Label htmlFor="name">Full Name</Label>
            <Input id="name" placeholder="John Doe" />
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="dob">Date of Birth</Label>
            <Input id="dob" type="date" />
          </div>

          <div className="flex flex-col gap-2">
            <Label htmlFor="contact">Contact Info</Label>
            <Input id="contact" placeholder="Email or Phone Number" />
          </div>
        </div>
      </ResizablePanel>

      <ResizableHandle />

      {/* Section Two & Three Grouped Vertically */}
      <ResizablePanel defaultSize={50}>
        <ResizablePanelGroup direction="vertical">
          {/* Section Two - ID Upload */}
          <ResizablePanel defaultSize={25}>
            <div className="flex flex-col gap-4 h-full justify-center p-6">
              <h2 className="text-lg font-semibold">Upload ID</h2>
              <Input type="file" accept="image/*" />
              <p className="text-sm text-muted-foreground">Accepted formats: PNG, JPG</p>
            </div>
          </ResizablePanel>

          <ResizableHandle />

          {/* Section Three - Family Doctor */}
          <ResizablePanel defaultSize={75}>
            <div className="flex flex-col gap-4 h-full justify-center p-6">
              <h2 className="text-lg font-semibold">Family Doctor</h2>

              <div className="flex flex-col gap-2">
                <Label htmlFor="doctor-name">Doctor's Name</Label>
                <Input id="doctor-name" placeholder="Dr. Smith" />
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="clinic">Clinic or Hospital</Label>
                <Input id="clinic" placeholder="Sunrise Medical Centre" />
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea id="notes" placeholder="Any extra information..." />
              </div>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </ResizablePanel>
    </ResizablePanelGroup>
  );
}
